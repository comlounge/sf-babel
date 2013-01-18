from sfext.babel import T, Babel, babel_module
from starflyer import Application, Handler, URL

class TestHandler2(Handler):
    """dummy handler""" 

    def get_locale(self):
        """return the locale"""
        print self.request.args
        return self.request.args['lang']

    def get(self):
        lang = self.request.args['lang']
        file = self.request.args['file']
        return self.render_lang(file)

def get_locale(handler):
    print handler
    print dir(handler)
    return handler.get_locale()

class App(Application):

    defaults = {
        'debug' : True,
        'testing' : True,
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

def test_missing_locale(app):
    c = app.test_client()
    rv = c.get("/", query_string="lang=de&file=emails/test2.txt")
    assert rv.data == "test2 en"

def test_locale2(app):
    c = app.test_client()
    rv = c.get("/", query_string="lang=en&file=emails/test1.txt")
    assert rv.data == "test en"
