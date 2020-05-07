import NAU7802, time, os, json

from http.server import HTTPServer, BaseHTTPRequestHandler

class balenaScales():
    myScale = NAU7802.NAU7802()
    zeroOffset = 0
    calibrationFactor = 0

    def __init__(self):
           if self.myScale.begin():
            if os.environ.get('CALIBRATION') != None and os.environ.get('ZERO_OFFSET') != None:
                self.calibrationFactor = float(os.environ.get('CALIBRATION'))
                self.myScale.setCalibrationFactor(self.calibrationFactor)
                self.zeroOffset = float(os.environ.get('ZERO_OFFSET'))
                self.myScale.setZeroOffset(self.zeroOffset)
            else:
                print("Entering calibration mode. Please follow these instructions:")
                time.sleep(5)
                print("Make sure the scale has no weight on it. And wait for the next prompt.")
                time.sleep(5)
                self.myScale.calculateZeroOffset(64)
                time.sleep(2)
                calibrationWeight = float(os.environ.get('CALIBRATION_WEIGHT')) or float(0.1)
                print("Place a " + str(calibrationWeight) + "g weight on the scale, and wait for the next prompt.")
                time.sleep(5)
                self.myScale.calculateCalibrationFactor(calibrationWeight, 64)
                calibrationFactor = self.myScale.getCalibrationFactor()
                print("Please set your CALIBRATION device variable to: " + str(calibrationFactor))
                print("Please set your ZERO_OFFSET device variable to: " + str(self.myScale.getZeroOffset()))
                exit()

    def sample(self):
        if self.myScale.begin():
            time.sleep(1) # sometimes the scales aren't ready to read. No need to rush them!
            self.currentWeight = self.myScale.getWeight()
            currentReading = self.myScale.getReading()

            print("Reading = %.2f" % currentReading)
            print("Weight = %.2f" % self.currentWeight)

            return [
                {
                    'measurement': 'balena-scales',
                    'fields': {
                        'weight': float(self.currentWeight)
                    }
                }
            ]
        else:
            print("Scales cannot be detected. Exiting!")
            exit()



class balenaScalesHTTP(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        measurements = balenascales.sample()
        self.wfile.write(json.dumps(measurements[0]['fields']).encode('UTF-8'))

    def do_HEAD(self):
        self._set_headers()


# Start the server to answer requests for readings
balenascales = balenaScales()

while True:
    server_address = ('', 80)
    httpd = HTTPServer(server_address, balenaScalesHTTP)
    print('Scales HTTP server running')
    httpd.serve_forever()
