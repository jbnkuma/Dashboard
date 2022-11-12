from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.log import enable_pretty_logging
import werkzeug.serving
from werkzeug.debug import DebuggedApplication

from reports_manager.dashboard import app


@werkzeug.serving.run_with_reloader
def run_server():
    app.debug = True
    application = DebuggedApplication(app, evalex=True)
    http_server = HTTPServer(WSGIContainer(application, enable_pretty_logging(options='', logger='')))
    http_server.listen(5000)
    enable_pretty_logging()
    IOLoop.instance().start()


run_server()
