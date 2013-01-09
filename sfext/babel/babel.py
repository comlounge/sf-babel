# -*- coding: utf-8 -*-

"""
    sf-babel
    ~~~~~~~~

    Implements i18n/l10n support for starflyer applications based on Babel.

    :copyright: (c) 2013 by Christian Scholz, based on code by Armin Ronacher in flask-babel.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import absolute_import
import os

# this is a workaround for a snow leopard bug that babel does not
# work around :)

if os.environ.get('LC_CTYPE', '').lower() == 'utf-8':
    os.environ['LC_CTYPE'] = 'en_US.utf-8'

from datetime import datetime
from babel import dates, numbers, support, Locale
from starflyer import Module, AttributeMapper                                                                                                                                            
import pkg_resources

from werkzeug import ImmutableDict

try:
    from pytz.gae import pytz
except ImportError:
    from pytz import timezone, UTC
else:
    timezone = pytz.timezone
    UTC = pytz.UTC

class Babel(Module):
    """i18n support for starflyer applications.

    In order to set the locale on a request basis you should create a function ``get_local()`` inside your 
    handler and to set the timezone a function ``get_timezone()`` accordingly. The former can look like follows::

        def get_locale():
            # if a user is logged in, use the locale from the user settings
            if self.user is not None: # like it would work with userbase
                return user.locale
            # otherwise try to guess the language from the user accept
            # header the browser transmits.  We support de/fr/en in this
            # example.  The best match wins.
            return self.request.accept_languages.best_match(['de', 'fr', 'en'])

    For timezones it might look like this::

        def get_timezone():
            if self.user is not None:
                return self.user.timezone
        
    """

    name = "babel"

    default_date_formats = ImmutableDict({
        'time':             'medium',
        'date':             'medium',
        'datetime':         'medium',
        'time.short':       None,
        'time.medium':      None,
        'time.full':        None,
        'time.long':        None,
        'date.short':       None,
        'date.medium':      None,
        'date.full':        None,
        'date.long':        None,
        'datetime.short':   None,
        'datetime.medium':  None,
        'datetime.full':    None,
        'datetime.long':    None,
    })

    defaults = {
        'default_locale'    : 'en',
        'default_timezone'  : 'UTC',
        'date_formats'      : None,
        'configure_jinja'   : True,
        'locale_selector_func' : None,
        'timezone_selector_func' : None,
    }

    def finalize(self):

        # set date formats
        if self.config.date_formats is None:
            self.config.date_formats = self.default_date_formats.copy()

        #: a mapping of Babel datetime format strings that can be modified
        #: to change the defaults.  If you invoke :func:`format_datetime`
        #: and do not provide any format string sf-babel will do the
        #: following things:
        #:
        #: 1.   look up ``date_formats['datetime']``.  By default ``'medium'``
        #:      is returned to enforce medium length datetime formats.
        #: 2.   ``date_formats['datetime.medium'] (if ``'medium'`` was
        #:      returned in step one) is looked up.  If the return value
        #:      is anything but `None` this is used as new format string.
        #:      otherwise the default for that language is used.
        self.date_formats = self.config.date_formats


        app = self.app

        if self.config.configure_jinja:
            app.jinja_env.filters.update(
                datetimeformat=format_datetime,
                dateformat=format_date,
                timeformat=format_time,
                timedeltaformat=format_timedelta,
                numberformat=format_number,
                decimalformat=format_decimal,
                currencyformat=format_currency,
                percentformat=format_percent,
                scientificformat=format_scientific,
            )
            app.jinja_env.add_extension('jinja2.ext.i18n')
            #app.jinja_env.install_gettext_callables(
                #lambda x: self.get_translations().ugettext(x),
                #lambda s, p, n: self.get_translations().ungettext(s, p, n),
                #newstyle=True
            #)

    def get_render_context(self, handler):
        """pass in gettext and ungettext into the local namespace."""
        return dict(
                gettext = self.get_translations(handler).ugettext,
                ngettext = self.get_translations(handler).ungettext,
        )

    def list_translations(self):
        """Returns a list of all the locales translations exist for.  The
        list returned will be filled with actual locale objects and not just
        strings.

        .. versionadded:: 0.6
        """
        dirname = os.path.join(self.app.root_path, 'translations')
        if not os.path.isdir(dirname):
            return []
        result = []
        for folder in os.listdir(dirname):
            locale_dir = os.path.join(dirname, folder, 'LC_MESSAGES')
            if not os.path.isdir(locale_dir):
                continue
            if filter(lambda x: x.endswith('.mo'), os.listdir(locale_dir)):
                result.append(Locale.parse(folder))
        if not result:
            result.append(Locale.parse(self._default_locale))
        return result

    @property
    def default_locale(self):
        """The default locale from the configuration as instance of a
        `babel.Locale` object.
        """
        return Locale.parse(self.config['default_locale'])

    @property
    def default_timezone(self):
        """The default timezone from the configuration as instance of a
        `pytz.timezone` object.
        """
        return timezone(self.config['default_timezone'])


    def get_translations(self, handler):
        """Returns the correct gettext translations that should be used for
        this request.  This will never fail and return a dummy translation
        object if used outside of the request or if a translation cannot be
        found.
        """
        #translations = getattr(ctx, 'babel_translations', None)
        translations = getattr(handler, "babel_translations", None)
        print 1
        print translations
        if translations is None:
            dirname = pkg_resources.resource_filename(self.app.import_name, "translations")
            translations = support.Translations.load(dirname, [self.get_locale(handler)])
            print self.get_locale(handler)
            handler.babel_translations = translations
        return translations


    def get_locale(self, handler):
        """Returns the locale that should be used for this request as
        `babel.Locale` object.  This returns `None` if used outside of
        a request.
        """
        locale = getattr(handler, 'babel_locale', None)
        if locale is None:
            if not hasattr(handler, "get_locale"):
                locale = self.default_locale
            else:
                rv = handler.get_locale()
                if rv is None:
                    locale = self.default_locale
                else:
                    locale = Locale.parse(rv)
            handler.babel_locale = locale
        return locale


def get_timezone():
    """Returns the timezone that should be used for this request as
    `pytz.timezone` object.  This returns `None` if used outside of
    a request.
    """
    ctx = _request_ctx_stack.top
    tzinfo = getattr(ctx, 'babel_tzinfo', None)
    if tzinfo is None:
        babel = ctx.app.extensions['babel']
        if babel.timezone_selector_func is None:
            tzinfo = babel.default_timezone
        else:
            rv = babel.timezone_selector_func()
            if rv is None:
                tzinfo = babel.default_timezone
            else:
                if isinstance(rv, basestring):
                    tzinfo = timezone(rv)
                else:
                    tzinfo = rv
        ctx.babel_tzinfo = tzinfo
    return tzinfo


def refresh():
    """Refreshes the cached timezones and locale information.  This can
    be used to switch a translation between a request and if you want
    the changes to take place immediately, not just with the next request::

        user.timezone = request.form['timezone']
        user.locale = request.form['locale']
        refresh()
        flash(gettext('Language was changed'))

    Without that refresh, the :func:`~flask.flash` function would probably
    return English text and a now German page.
    """
    ctx = _request_ctx_stack.top
    for key in 'babel_locale', 'babel_tzinfo', 'babel_translations':
        if hasattr(ctx, key):
            delattr(ctx, key)


def _get_format(key, format):
    """A small helper for the datetime formatting functions.  Looks up
    format defaults for different kinds.
    """
    babel = _request_ctx_stack.top.app.extensions['babel']
    if format is None:
        format = babel.date_formats[key]
    if format in ('short', 'medium', 'full', 'long'):
        rv = babel.date_formats['%s.%s' % (key, format)]
        if rv is not None:
            format = rv
    return format


def to_user_timezone(datetime):
    """Convert a datetime object to the user's timezone.  This automatically
    happens on all date formatting unless rebasing is disabled.  If you need
    to convert a :class:`datetime.datetime` object at any time to the user's
    timezone (as returned by :func:`get_timezone` this function can be used).
    """
    if datetime.tzinfo is None:
        datetime = datetime.replace(tzinfo=UTC)
    tzinfo = get_timezone()
    return tzinfo.normalize(datetime.astimezone(tzinfo))


def to_utc(datetime):
    """Convert a datetime object to UTC and drop tzinfo.  This is the
    opposite operation to :func:`to_user_timezone`.
    """
    if datetime.tzinfo is None:
        datetime = get_timezone().localize(datetime)
    return datetime.astimezone(UTC).replace(tzinfo=None)


def format_datetime(datetime=None, format=None, rebase=True):
    """Return a date formatted according to the given pattern.  If no
    :class:`~datetime.datetime` object is passed, the current time is
    assumed.  By default rebasing happens which causes the object to
    be converted to the users's timezone (as returned by
    :func:`to_user_timezone`).  This function formats both date and
    time.

    The format parameter can either be ``'short'``, ``'medium'``,
    ``'long'`` or ``'full'`` (in which cause the language's default for
    that setting is used, or the default from the :attr:`Babel.date_formats`
    mapping is used) or a format string as documented by Babel.

    This function is also available in the template context as filter
    named `datetimeformat`.
    """
    format = _get_format('datetime', format)
    return _date_format(dates.format_datetime, datetime, format, rebase)


def format_date(date=None, format=None, rebase=True):
    """Return a date formatted according to the given pattern.  If no
    :class:`~datetime.datetime` or :class:`~datetime.date` object is passed,
    the current time is assumed.  By default rebasing happens which causes
    the object to be converted to the users's timezone (as returned by
    :func:`to_user_timezone`).  This function only formats the date part
    of a :class:`~datetime.datetime` object.

    The format parameter can either be ``'short'``, ``'medium'``,
    ``'long'`` or ``'full'`` (in which cause the language's default for
    that setting is used, or the default from the :attr:`Babel.date_formats`
    mapping is used) or a format string as documented by Babel.

    This function is also available in the template context as filter
    named `dateformat`.
    """
    if rebase and isinstance(date, datetime):
        date = to_user_timezone(date)
    format = _get_format('date', format)
    return _date_format(dates.format_date, date, format, rebase)


def format_time(time=None, format=None, rebase=True):
    """Return a time formatted according to the given pattern.  If no
    :class:`~datetime.datetime` object is passed, the current time is
    assumed.  By default rebasing happens which causes the object to
    be converted to the users's timezone (as returned by
    :func:`to_user_timezone`).  This function formats both date and
    time.

    The format parameter can either be ``'short'``, ``'medium'``,
    ``'long'`` or ``'full'`` (in which cause the language's default for
    that setting is used, or the default from the :attr:`Babel.date_formats`
    mapping is used) or a format string as documented by Babel.

    This function is also available in the template context as filter
    named `timeformat`.
    """
    format = _get_format('time', format)
    return _date_format(dates.format_time, time, format, rebase)


def format_timedelta(datetime_or_timedelta, granularity='second'):
    """Format the elapsed time from the given date to now or the given
    timedelta.  This currently requires an unreleased development
    version of Babel.

    This function is also available in the template context as filter
    named `timedeltaformat`.
    """
    if isinstance(datetime_or_timedelta, datetime):
        datetime_or_timedelta = datetime.utcnow() - datetime_or_timedelta
    return dates.format_timedelta(datetime_or_timedelta, granularity,
                                  locale=get_locale())


def _date_format(formatter, obj, format, rebase, **extra):
    """Internal helper that formats the date."""
    locale = get_locale()
    extra = {}
    if formatter is not dates.format_date and rebase:
        extra['tzinfo'] = get_timezone()
    return formatter(obj, format, locale=locale, **extra)


def format_number(number):
    """Return the given number formatted for the locale in request
    
    :param number: the number to format
    :return: the formatted number
    :rtype: unicode
    """
    locale = get_locale()
    return numbers.format_number(number, locale=locale)


def format_decimal(number, format=None):
    """Return the given decimal number formatted for the locale in request

    :param number: the number to format
    :param format: the format to use
    :return: the formatted number
    :rtype: unicode
    """
    locale = get_locale()
    return numbers.format_decimal(number, format=format, locale=locale)


def format_currency(number, currency, format=None):
    """Return the given number formatted for the locale in request

    :param number: the number to format
    :param currency: the currency code
    :param format: the format to use
    :return: the formatted number
    :rtype: unicode
    """
    locale = get_locale()
    return numbers.format_currency(
        number, currency, format=format, locale=locale
    )


def format_percent(number, format=None):
    """Return formatted percent value for the locale in request

    :param number: the number to format
    :param format: the format to use
    :return: the formatted percent number
    :rtype: unicode
    """
    locale = get_locale()
    return numbers.format_percent(number, format=format, locale=locale)


def format_scientific(number, format=None):
    """Return value formatted in scientific notation for the locale in request

    :param number: the number to format
    :param format: the format to use
    :return: the formatted percent number
    :rtype: unicode
    """
    locale = get_locale()
    return numbers.format_scientific(number, format=format, locale=locale)


def gettext(string, **variables):
    """Translates a string with the current locale and passes in the
    given keyword arguments as mapping to a string formatting string.

    ::

        gettext(u'Hello World!')
        gettext(u'Hello %(name)s!', name='World')
    """
    t = get_translations()
    if t is None:
        return string % variables
    return t.ugettext(string) % variables
_ = gettext


def ngettext(singular, plural, num, **variables):
    """Translates a string with the current locale and passes in the
    given keyword arguments as mapping to a string formatting string.
    The `num` parameter is used to dispatch between singular and various
    plural forms of the message.  It is available in the format string
    as ``%(num)d`` or ``%(num)s``.  The source language should be
    English or a similar language which only has one plural form.

    ::

        ngettext(u'%(num)d Apple', u'%(num)d Apples', num=len(apples))
    """
    variables.setdefault('num', num)
    t = get_translations()
    if t is None:
        return (singular if num == 1 else plural) % variables
    return t.ungettext(singular, plural, num) % variables


def pgettext(context, string, **variables):
    """Like :func:`gettext` but with a context.

    .. versionadded:: 0.7
    """
    t = get_translations()
    if t is None:
        return string % variables
    return t.upgettext(context, string) % variables


def npgettext(context, singular, plural, num, **variables):
    """Like :func:`ngettext` but with a context.

    .. versionadded:: 0.7
    """
    variables.setdefault('num', num)
    t = get_translations()
    if t is None:
        return (singular if num == 1 else plural) % variables
    return t.unpgettext(context, singular, plural, num) % variables


def lazy_gettext(string, **variables):
    """Like :func:`gettext` but the string returned is lazy which means
    it will be translated when it is used as an actual string.

    Example::

        hello = lazy_gettext(u'Hello World')

        @app.route('/')
        def index():
            return unicode(hello)
    """
    from speaklater import make_lazy_string
    return make_lazy_string(gettext, string, **variables)


def lazy_pgettext(context, string, **variables):
    """Like :func:`pgettext` but the string returned is lazy which means
    it will be translated when it is used as an actual string.

    .. versionadded:: 0.7
    """
    from speaklater import make_lazy_string
    return make_lazy_string(pgettext, context, string, **variables)



babel_module = Babel(__name__)

