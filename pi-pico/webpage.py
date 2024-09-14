from microdot import Microdot, send_file
from storage import Storage

app = Microdot()

@app.route('/')
async def index(request):
    return send_file('static/index.html')

@app.route('/static/<path:path>')
async def static(request, path):
    if '..' in path:
        # directory traversal is not allowed
        return 'Not found', 404
    return send_file('static/' + path, max_age=3600)

@app.get('/shutdown')
async def shutdown(request):
    request.app.shutdown()
    return 'The server is shutting down...'