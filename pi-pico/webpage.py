from microdot import Microdot, send_file
from storage import Storage

app = Microdot()

@app.route('/')
async def index(request):
    return "Hello, WaterBox!"

@app.route('/static/<path:path>')
async def static(request, path):
    if '..' in path:
        # directory traversal is not allowed
        return 'Not found', 404
    return send_file(path, max_age=86400)

@app.get('/shutdown')
async def shutdown(request):
    request.app.shutdown()
    return 'The server is shutting down...'