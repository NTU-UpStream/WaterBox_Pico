from microdot import Microdot, send_file, Response, Request
from storage import Storage
from config import WaterBoxConfig
import json
import machine

try:
    from waterbox import WaterBox
except ImportError:
    pass

class WaterBoxWebPage(Microdot):
    def __init__(self, box: WaterBox):
        super().__init__()
        self.box = box
        self.led = machine.Pin("LED", machine.Pin.OUT)
        
        self.route('/')(self.index)
        self.route('/config')(self.config)
        self.route('/config/current')(self.config_current)
        self.route('/config/submit', methods=['POST'])(self.submit_config)
        self.route('/static/<path:path>')
        self.route('/shutdown')(self.shutdown)
        self.route('/monitor')(self.monitoring)
        self.route('/analog_values')(self.analog_values)
        self.route('/wifi_status')(self.wifi_status)
        self.route('/mqtt_connect')(self.mqtt_connect)
        self.route('/toggle_led')(self.toggle_led)

    async def index(self, request):
        return send_file('static/index.html')

    async def config(self, request):
        return send_file('static/config.html')
    
    async def submit_config(self, request):
        try:
            # Parse JSON data from the request body
            new_config = request.json
            print(new_config)

            if not new_config:
                return Response(json.dumps({"error": "No data received"}), status_code=400)

            # Update the configuration
            config_buffer = self.box.config.copy()
            config_buffer.update(new_config)

            # Save the config
            self.box.storage.save_config(config_buffer)
            self.box.reload_config()

            return Response(json.dumps({"message": "Configuration updated successfully"}), status_code=200)
        except Exception as e:
            return Response(json.dumps({"error": str(e)}), status_code=500)

    async def config_current(self, request):
        return Response(json.dumps(self.box.config))
        
    async def static(self, request, path):
        if '..' in path:
            # directory traversal is not allowed
            return 'Not found', 404
        return send_file('static/' + path, max_age=3600)

    def shutdown(self, request):
        request.app.shutdown()
        return 'The server is shutting down...'

    async def monitoring(self, request):
        return send_file('static/monitoring.html')
    
    async def analog_values(self, request):
        values = self.box.analog.read_all()
        
        # Ensure we have a list of 4 numbers
        if not isinstance(values, list) or len(values) != 4:
            return Response(json.dumps({"error": "Invalid analog values"}), status_code=500)
        
        # Convert to a list of floats (which are always JSON-serializable)
        serializable_values = [float(v) for v in values]
        return Response(json.dumps(serializable_values))
    
    async def wifi_status(self, request):
        status = self.box.wifiman.status()
        return Response(status)

    async def mqtt_connect(self, request):
        result = self.box.mqtt.connect()
        print(result)
        return Response(json.dumps({"result": result}))

    async def toggle_led(self, request):
        self.led.toggle()
        return Response(json.dumps({"led_state": self.led.value()}))