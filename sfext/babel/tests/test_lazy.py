
from sfext.babel import T, Babel, babel_module
from starflyer import Application, Handler, URL

class App(Application):

    defaults = {
        'testing' : True,
    }

    modules = [
        babel_module()
    ]

TEST_STRING = T("foo")

class TestHandler(Handler):
    """dummy handler""" 
    def get_locale(self):
        """return the locale"""
        return self.request.args.get('lang', 'en')


def test_lazy():
    app = App(__name__)
    handler = TestHandler(app, app.request_class({}))
    gt = app.module_map['babel'].gettext
    assert app.module_map['babel'].gettext(handler, TEST_STRING) == "bar"


