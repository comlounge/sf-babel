from starflyer import Module, Handler, URL

class TestHandler(Handler):

    def get_locale(self):
        """return the locale from the reqzest or the default"""
        return self.request.args.get('lang', 'en')

    def get(self):
        """retrieve the file given by the request file attrib"""
        lang = self.request.args.get('lang', 'en')
        file = self.request.args['file']
        return self.render_lang(file)


class Handler1(Handler):
    template = "test1"

class Handler2(Handler):
    template = "test2"

class TestModule(Module):
    """test module with 2 routes"""

    name = "test"

    routes = [
        URL("/", "test_generic", TestHandler),
        URL("/1", "test1", Handler1),
        URL("/2", "test2", Handler2),
    ]

mod = TestModule(__name__)
