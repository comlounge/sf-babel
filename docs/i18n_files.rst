=============================
Complete Template translation
=============================

Sometimes you not only have simple strings to translate but maybe a full template like
an email template. In these cases you might not want to translate each string separately 
but instead simply provide an email template per language.

Filesystem setup
================

First of all you need a folder with subfolders for each language you want to support, e.g.::

    emails/
    emails/de
    emails/en
    emails/es

and so on.

You also might want to choose a default locale for which you provide the email templates first.
You then simply drop your email templates into these subfolders, e.g.::

    emails/en/subscription.txt

In your application class you then need to define a loader for those templates::

    def finalize_setup(self):
        # both are equivalent, the loader will be created automatically in the second case
        self.module_map.babel.register_env("emails", jinja2.Environment(loader = LanguagePrefixLoader(__name__, "templates/emails"))
        self.module_map.babel.register_dir("emails", "templates/emails")


Different idea
==============

Another idea is to not use a different environment but use the application's environment for it. Imagine you have a folder
``templates/emails`` and you want to load the localized email template for ``subscription.txt``. You would then write::

    self.module_map.babel.get_template("emails/subscription.txt")

This will then split the path into elements and search for a localized version in sub folders in ``emails/``.
As an example imagine we have a locale of "de" and a default locale "en". We will have the following folder setup::

    templates/emails/en/subscription.txt
    templates/emails/de/

(and thus no ``subcription.txt`` in the requested locale).

sf-babel would then do the following when being asked for ``emails/subscription.txt``:

1. Split the path into components, marking the last element as filename.
2. Take the requested locale ``de`` and build a new path from the first path elements, followed by the language code, followed by the filename. 
3. If it is not found, it will do the same for the default locale.


Modules
=======

This also works in modules but in modules we have more paths to consider when searching a template. We search for it in the following order:

- the chosen locale in the apps module specific templates (e.g. /_m/<module_name>/<file>)




Usage
=====

Now if you want to use a template you simply ask the babel module for it::
    
    tmpl = self.module_map.babel.get_template("emails", "subscription.txt") 

This call will do the following:

    1. Call the ``get_locale()`` function to get the locale to use (or the default locale)
    2. If ``subscription.txt`` is available in ``templates/emails/<locale>`` then return it
    3. if not, try the default locale's folder and get the template from there



