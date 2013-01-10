
from sfext.babel import T, Babel, babel_module
from starflyer import Application, Handler

class App(Application):

    modules = [
        babel_module()
    ]

TEST_STRING = T("foo")

class TestHandler(Handler):
    """dummy handler""" 

def test_lazy():
    app = App(__name__)
    handler = TestHandler(app, app.request_class({}))
    gt = app.module_map['babel'].gettext
    assert app.module_map['babel'].gettext(handler, TEST_STRING) == "bar"


