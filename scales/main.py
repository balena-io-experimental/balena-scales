import NAU7802, time, os, json

from http.server import HTTPServer, BaseHTTPRequestHandler

class balenaScales():
    myScale = NAU7802.NAU7802()
    weightOffset = 0
    zeroOffset = 0
    calibrationFactor = 0

    def __init__(self):
           if self.myScale.begin():
            if os.environ.get('CALIBRATION') != None and os.environ.get('ZERO_OFFSET') != None and os.environ.get('WEIGHT_OFFSET') != None:
                calibrationFactor = float(os.environ.get('CALIBRATION'))
                self.myScale.setCalibrationFactor(calibrationFactor)
                self.myScale.setZeroOffset(float(os.environ.get('ZERO_OFFSET')))
                self.weightOffset = float(os.environ.get('WEIGHT_OFFSET'))
            else:
                print("Entering calibration mode. Please follow these instructions:")
                time.sleep(5)
                print("Make sure the scale has no weight on it. And wait for the next prompt.")
                time.sleep(5)
                self.myScale.calculateZeroOffset(64)
                # print("Calculated zero offset = " + str(myScale.getZeroOffset()))
                time.sleep(2)
                print("Place a 200g weight on the scale, and wait for the next prompt.")
                time.sleep(5)
                self.myScale.calculateCalibrationFactor(200.0, 64)
                calibrationFactor = self.myScale.getCalibrationFactor()
                # print("New calibration factor: " + str(myScale.getCalibrationFactor()))
                time.sleep(2)
                # print("New Scale Reading: " + str(myScale.getWeight()))
                zeroWeight = self.myScale.getWeight()- 200
                print("Please set your CALIBRATION device variable to: " + str(calibrationFactor))
                print("Please set your ZERO_OFFSET device variable to: " + str(self.myScale.getZeroOffset()))
                print("Please set your WEIGHT_OFFSET device variable to: " + str(zeroWeight))
                exit()

    def sample(self):
        if self.myScale.begin():
            time.sleep(1) # sometimes the scales aren't ready to read. No need to rush them!
            self.currentWeight = self.myScale.getWeight()
            # print('Weight reading:' + str(currentWeight))
            self.calculatedWeight = self.currentWeight - self.weightOffset
            print("Weight = %.2f" % self.calculatedWeight + " grams")
            return [
                {
                    'measurement': 'balena-scales',
                    'fields': {
                        'weight': float(self.calculatedWeight)
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
