from tornado.web import RequestHandler, Application

from tests.utils import read


class Index(RequestHandler):
    async def get(self):
        self.set_header('Content-Type', 'text/plain')
        self.finish('Hello Tornado!')


class Html(RequestHandler):
    async def get(self):
        self.set_header('Content-Type', 'text/html')
        self.finish(read('simple.html'))


class Form(RequestHandler):
    async def post(self):
        self.set_header('Content-Type', 'text/plain')
        self.finish(self.get_body_argument('field'))


def build_app():
    return Application([
        ('/', Index),
        ('/html/', Html),
        ('/form/', Form)
    ])
