from microdot import Microdot, send_file
from storage import Storage

try:
    from waterbox import WaterBox
except ImportError:
    pass

class WaterBoxWebPage(Microdot):
    def __init__(self, box: WaterBox):
        super().__init__()
        self.box = box

        self.route('/', self.index)

    def add_routes(self, url_pattern, methods):
        pass

    def index(self, request):
        return send_file('static/index.html')

    def config(self, request):
        return send_file('static/config.html')

    def static(self, request, path):
        if '..' in path:
            # directory traversal is not allowed
            return 'Not found', 404
        return send_file('static/' + path, max_age=3600)

    def shutdown(self, request):
        request.app.shutdown()
        return 'The server is shutting down...'