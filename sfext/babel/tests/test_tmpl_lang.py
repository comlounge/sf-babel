from sfext.babel import T, Babel, babel_module
from starflyer import Application, Handler, URL, Module
from mods.tm import mod 

class TestHandler2(Handler):
    """dummy handler""" 

    def get_locale(self):
        """return the locale"""
        return self.request.args.get('lang', 'en')

    def get(self):
        lang = self.request.args.get('lang', 'en')
        file = self.request.args['file']
        return self.render_lang(file)

def get_locale(handler):
    return handler.get_locale()

class App(Application):

    defaults = {
        'debug' : True,
        'testing' : True,
        'secret_key' : 'secret',
        'force_exceptions' : True,
    }

    modules = [
        babel_module(
            default_locale       = 'en',
            locale_selector_func = get_locale,
        )
    ]
    routes = [
        URL("/", "root", TestHandler2)
    ]

def pytest_funcarg__app(request):
    return App(__name__)

def test_correct_locale(app):
    c = app.test_client()
    rv = c.get("/", query_string="lang=de&file=emails/test1.txt")
    assert rv.data == "test de"

def test_missing_localized_template(app):
    # text2 only exists in en, so this should be taken
    c = app.test_client()
    rv = c.get("/", query_string="lang=de&file=emails/test2.txt")
    assert rv.data == "test2 en"

def test_locale2(app):
    c = app.test_client()
    rv = c.get("/", query_string="lang=en&file=emails/test1.txt")
    assert rv.data == "test en"

def test_missing_locale_info(app):
    # we use the default local definition here which should be en
    c = app.test_client()
    rv = c.get("/", query_string="file=emails/test1.txt")
    assert rv.data == "test en"


"""
now we test module support, e.g. when a module is about to use render_lang.

We have to test the basic cases against the module. Everything is then happening
inside the module's templates directory.

"""

class ModuleApp(Application):

    defaults = {
        'debug' : True,
        'testing' : True,
        'secret_key' : 'secret',
        'force_exceptions' : True,
    }

    modules = [
        mod(),
        babel_module(
            default_locale       = 'en',
            locale_selector_func = get_locale,
        )
    ]
    routes = [
    ]

def pytest_funcarg__mapp(request):
    return ModuleApp(__name__)

def test_module_correct_locale(mapp):
    c = mapp.test_client()
    rv = c.get("/test/", query_string="lang=de&file=emails/test1.txt")
    assert rv.data == "module test 1 de"

def test_module_missing_localized_template(mapp):
    # text2 only exists in en, so this should be taken
    c = mapp.test_client()
    rv = c.get("/test/", query_string="lang=de&file=emails/test2.txt")
    assert rv.data == "module test 2 en"

def test_module_locale2(mapp):
    c = mapp.test_client()
    rv = c.get("/test/", query_string="lang=en&file=emails/test1.txt")
    assert rv.data == "module test 1 en"

def test_module_missing_locale_info(mapp):
    # we use the default local definition here which should be en
    c = mapp.test_client()
    rv = c.get("/test/", query_string="file=emails/test1.txt")
    assert rv.data == "module test 1 en"


# now check if we can override lang files in the app, we test this with a test 3
# which also exists in the emails/en/test3.txt location in the app

def test_module_app_override(mapp):
    c = mapp.test_client()
    rv = c.get("/test/", query_string="lang=en&file=emails/test3.txt")
    assert rv.data == "app test 3 en"


