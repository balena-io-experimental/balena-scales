import NAU7802, time, os, json

myScale = NAU7802.NAU7802()
time.sleep(1) # sometimes the scales aren't ready to read. No need to rush them!
if myScale.begin():
    while(True):
        currentReading = myScale.getReading()
        print(str(currentReading))
        input("Press a key...")
