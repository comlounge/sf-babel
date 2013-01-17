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

Now if you want to use a template you simply ask the babel module for it::
    
    tmpl = self.module_map.babel.get_template("emails", "subscription.txt") 

This call will do the following:

    1. Call the ``get_locale()`` function to get the locale to use (or the default locale)
    2. If ``subscription.txt`` is available in ``templates/emails/<locale>`` then return it
    3. if not, try the default locale's folder and get the template from there
