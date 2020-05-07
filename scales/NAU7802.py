import smbus2
import time

Scale_Registers = {'NAU7802_PU_CTRL': 0x00,
                   'NAU7802_CTRL1': 1,
                   'NAU7802_CTRL2': 2,
                   'NAU7802_OCAL1_B2': 3,
                   'NAU7802_OCAL1_B1': 4,
                   'NAU7802_OCAL1_B0': 5,
                   'NAU7802_GCAL1_B3': 6,
                   'NAU7802_GCAL1_B2': 7,
                   'NAU7802_GCAL1_B1': 8,
                   'NAU7802_GCAL1_B0': 9,
                   'NAU7802_OCAL2_B2': 10,
                   'NAU7802_OCAL2_B1': 11,
                   'NAU7802_OCAL2_B0': 12,
                   'NAU7802_GCAL2_B3': 13,
                   'NAU7802_GCAL2_B2': 14,
                   'NAU7802_GCAL2_B1': 15,
                   'NAU7802_GCAL2_B0': 16,
                   'NAU7802_I2C_CONTROL': 17,
                   'NAU7802_ADCO_B2': 18,
                   'NAU7802_ADCO_B1': 19,
                   'NAU7802_ADCO_B0': 20,
                   'NAU7802_ADC': 0x15,
                   'NAU7802_OTP_B1': 22,
                   'NAU7802_OTP_B0': 23,
                   'NAU7802_PGA': 0x1B,
                   'NAU7802_PGA_PWR': 0x1C,
                   'NAU7802_DEVICE_REV': 0x1F}

# Bits within the PU_CRTL register
PU_CTRL_Bits = {'NAU7802_PU_CTRL_RR': 0,
                'NAU7802_PU_CTRL_PUD': 1,
                'NAU7802_PU_CTRL_PUA': 2,
                'NAU7802_PU_CTRL_PUR': 3,
                'NAU7802_PU_CTRL_CS': 4,
                'NAU7802_PU_CTRL_CR': 5,
                'NAU7802_PU_CTRL_OSCS': 6,
                'NAU7802_PU_CTRL_AVDDS': 7}

# Bits within the CTRL1 register
CTRL1_Bits = {'NAU7802_CTRL1_GAIN': 2,
              'NAU7802_CTRL1_VLDO': 5,
              'NAU7802_CTRL1_DRDY_SEL': 6,
              'NAU7802_CTRL1_CRP': 7}

# Bits within the CTRL2 register
CTRL2_Bits = {'NAU7802_CTRL2_CALMOD': 0,
              'NAU7802_CTRL2_CALS': 2,
              'NAU7802_CTRL2_CAL_ERROR': 3,
              'NAU7802_CTRL2_CRS': 4,
              'NAU7802_CTRL2_CHS': 7}

# Bits within the PGA register
PGA_Bits = {'NAU7802_PGA_CHP_DIS': 0,
            'NAU7802_PGA_INV': 3,
            'NAU7802_PGA_BYPASS_EN': 4,
            'NAU7802_PGA_OUT_EN': 5,
            'NAU7802_PGA_LDOMODE': 6,
            'NAU7802_PGA_RD_OTP_SEL': 7}

# Bits within the PGA PWR register
PGA_PWR_Bits = {'NAU7802_PGA_PWR_PGA_CURR': 0,
                'NAU7802_PGA_PWR_ADC_CURR': 2,
                'NAU7802_PGA_PWR_MSTR_BIAS_CURR': 4,
                'NAU7802_PGA_PWR_PGA_CAP_EN': 7}

# Allowed Low drop out regulator voltages
NAU7802_LDO_Values = {'NAU7802_LDO_2V4': 0b111,
                      'NAU7802_LDO_2V7': 0b110,
                      'NAU7802_LDO_3V0': 0b101,
                      'NAU7802_LDO_3V3': 0b100,
                      'NAU7802_LDO_3V6': 0b011,
                      'NAU7802_LDO_3V9': 0b010,
                      'NAU7802_LDO_4V2': 0b001,
                      'NAU7802_LDO_4V5': 0b000}

# Allowed gains
NAU7802_Gain_Values = {'NAU7802_GAIN_128': 0b111,
                       'NAU7802_GAIN_64': 0b110,
                       'NAU7802_GAIN_32': 0b101,
                       'NAU7802_GAIN_16': 0b100,
                       'NAU7802_GAIN_8': 0b011,
                       'NAU7802_GAIN_4': 0b010,
                       'NAU7802_GAIN_2': 0b001,
                       'NAU7802_GAIN_1': 0b000}

# Allowed samples per second
NAU7802_SPS_Values = {'NAU7802_SPS_320': 0b111,
                      'NAU7802_SPS_80': 0b011,
                      'NAU7802_SPS_40': 0b010,
                      'NAU7802_SPS_20': 0b001,
                      'NAU7802_SPS_10': 0b000}

# Select between channel values
NAU7802_Channels = {'NAU7802_CHANNEL_1': 0,
                    'NAU7802_CHANNEL_2': 1}

# Calibration state
NAU7802_Cal_Status = {'NAU7802_CAL_SUCCESS': 0,
                      'NAU7802_CAL_IN_PROGRESS': 1,
                      'NAU7802_CAL_FAILURE': 2}

class NAU7802():
    def __init__(self, i2cPort = 1, deviceAddress = 0x2A, zeroOffset = False,
                 calibrationFactor = False):
        self.bus = smbus2.SMBus(i2cPort)
        self.deviceAddress = deviceAddress

        self.zeroOffset = zeroOffset
        self.calibrationFactor = calibrationFactor

    # Returns true if conversion complete
    def available(self):
        return self.getBit(PU_CTRL_Bits['NAU7802_PU_CTRL_CR'], Scale_Registers['NAU7802_PU_CTRL'])

    # Check calibration status.
    def calAFEStatus(self):
        if self.getBit(CTRL2_Bits['NAU7802_CTRL2_CALS'], Scale_Registers['NAU7802_CTRL2']):
            return NAU7802_Cal_Status['NAU7802_CAL_IN_PROGRESS']

        if self.getBit(CTRL2_Bits['NAU7802_CTRL2_CAL_ERROR'], Scale_Registers['NAU7802_CTRL2']):
            return NAU7802_Cal_Status['NAU7802_CAL_FAILURE']

        # Calibration passed
        return NAU7802_Cal_Status['NAU7802_CAL_SUCCESS']

    # Call when scale is setup, level, at running temperature, with nothing on it
    def calculateZeroOffset(self, averageAmount):    # Also called taring. Call this with nothing on the scale
        self.setZeroOffset(self.getAverage(averageAmount))

    # Calibrate analog front end of system. Returns true if CAL_ERR bit is 0 (no error)
    # Takes approximately 344ms to calibrate; wait up to 1000ms.
    # It is recommended that the AFE be re-calibrated any time the gain, SPS, or channel number is changed.
    def calibrateAFE(self): 
        self.beginCalibrateAFE()
        return self.waitForCalibrateAFE(1)

    # Sets up the NAU7802 for basic function
    # If initialize is true (or not specified), default init and calibration is performed
    # If initialize is false, then it's up to the caller to initalize and calibrate
    # Returns true upon completion
    def begin(self, initialized = True):    # Check communication and initialize sensor
        # Check if the device ack's over I2C
        if self.isConnected() == False:

            # There are rare times when the sensor is occupied and doesn't ack. A 2nd try resolves this.
            if self.isConnected() == False:
                print("Not connected")
                return False

        result = True    # Accumulate a result as we do the setup
        if initialized:
            result &= self.reset()    # Reset all registers
            result &= self.powerUp()    # Power on analog and digital sections of the scale
            result &= self.setLDO(NAU7802_LDO_Values['NAU7802_LDO_3V3'])    # Set LDO to 3.3V
            result &= self.setGain(NAU7802_Gain_Values['NAU7802_GAIN_128'])    # Set gain to 128
            result &= self.setSampleRate(NAU7802_SPS_Values['NAU7802_SPS_80'])     # Set samples per second to 10
            result &= self.setRegister(Scale_Registers['NAU7802_ADC'], 0x30)     # Turn off CLK_CHP. From 9.1 power on sequencing.
            result &= self.setBit(PGA_PWR_Bits['NAU7802_PGA_PWR_PGA_CAP_EN'], Scale_Registers['NAU7802_PGA_PWR'])     # Enable 330pF decoupling cap on chan 2. From 9.14 application circuit note.
            result &= self.calibrateAFE()     # Re-cal analog front end when we change gain, sample rate, or channel

        return result

    # Begin asynchronous calibration of the analog front end.
    # Poll for completion with calAFEStatus() or wait with waitForCalibrateAFE()
    def beginCalibrateAFE(self):   
        self.setBit(CTRL2_Bits['NAU7802_CTRL2_CALS'], Scale_Registers['NAU7802_CTRL2'])

    # Call after zeroing. Provide the float weight sitting on scale. Units do not matter.
    def calculateCalibrationFactor(self, weightOnScale, averageAmount):   
        onScale = self.getAverage(averageAmount)
        newCalFactor = (onScale - self.zeroOffset) / weightOnScale
        self.setCalibrationFactor(newCalFactor)

    # Mask & clear a given bit within a register
    def clearBit(self, bitNumber, registerAddress):
        value = self.getRegister(registerAddress)
        value &= ~(1 << bitNumber)    # Set this bit
        return self.setRegister(registerAddress, value)

    # Return the average of a given number of readings
    # Gives up after 1000ms so don't call this function to average 8 samples setup at 1Hz output (requires 8s)
    def getAverage(self, averageAmount):  
        total = 0
        samplesAcquired = 0

        startTime = time.time()
        while True:
            try:
                total += self.getReading()
            except:
                return False
            if samplesAcquired == averageAmount:
                break    # All done
            if time.time() - startTime > 1:
                return False    # Timeout - Bail with error
            samplesAcquired += 1
            time.sleep(0.001)
        total /= averageAmount
        return total

    # Return a given bit within a register
    def getBit(self, bitNumber, registerAddress):
        value = self.getRegister(registerAddress)
        value &= (1 << bitNumber)    # Clear all but this bit
        return value

    def getCalibrationFactor(self):    # Ask library for this value. Useful for storing value into NVM.
        return self.calibrationFactor

    # Returns 24-bit reading
    # Assumes CR Cycle Ready bit (ADC conversion complete) has been checked to be 1
    def getReading(self): 
        try:
            block = self.bus.read_i2c_block_data(self.deviceAddress, Scale_Registers['NAU7802_ADCO_B2'], 3)
            return int.from_bytes(block, "big", signed=True)
        except:
            return False

    # Get contents of a register
    def getRegister(self, registerAddress):
        try:
            return self.bus.read_i2c_block_data(self.deviceAddress, registerAddress, 1)[0]
        except:
            return False    # Error

    # Get the revision code of this IC
    def getRevisionCode(self): 
        revisionCode = self.getRegister(Scale_Registers['NAU7802_DEVICE_REV'])
        return revisionCode & 0x0F

    # Returns the y of y = mx + b using the current weight on scale, the cal factor, and the offset.
    # Once you've set zero offset and cal factor, you can ask the library to do the calculations for you.
    def getWeight(self, allowNegativeWeights = False, samplesToTake = 10):    
        onScale = self.getAverage(samplesToTake)

        # Prevent the current reading from being less than zero offset
        # This happens when the scale is zero'd, unloaded, and the load cell reports a value slightly less than zero value
        # causing the weight to be negative or jump to millions of pounds
        if allowNegativeWeights == False:
            if onScale < self.zeroOffset:
                onScale = self.zeroOffset    # Force reading to zero

        try:
            weight = (onScale - self.zeroOffset) / self.calibrationFactor
            return weight
        except:
            print('Needs calibrating')
            return False

    # Ask library for this value. Useful for storing value into NVM.
    def getZeroOffset(self):
        return self.zeroOffset

    # Returns true if device is present
    # Tests for device ack to I2C address
    def isConnected(self):
        try:
            self.bus.read_byte(self.deviceAddress)
            return True
        except:
            return False

    # Puts scale into low-power mode
    def powerDown(self):
        self.clearBit(PU_CTRL_Bits['NAU7802_PU_CTRL_PUD'], Scale_Registers['NAU7802_PU_CTRL'])
        return self.clearBit(PU_CTRL_Bits['NAU7802_PU_CTRL_PUA'], Scale_Registers['NAU7802_PU_CTRL'])

    # Power up digital and analog sections of scale
    def powerUp(self):
        self.setBit(PU_CTRL_Bits['NAU7802_PU_CTRL_PUD'], Scale_Registers['NAU7802_PU_CTRL'])
        self.setBit(PU_CTRL_Bits['NAU7802_PU_CTRL_PUA'], Scale_Registers['NAU7802_PU_CTRL'])

        # Wait for Power Up bit to be set - takes approximately 200us
        counter = 0
        while True:
            if self.getBit(PU_CTRL_Bits['NAU7802_PU_CTRL_PUR'], Scale_Registers['NAU7802_PU_CTRL']) != 0:
                break    # Good to go
            time.sleep(0.001)
            if counter > 100:
                return False    # Error
            counter += 1
        return True

    # Resets all registers to Power Of Defaults
    def reset(self):  
        self.setBit(PU_CTRL_Bits['NAU7802_PU_CTRL_RR'], Scale_Registers['NAU7802_PU_CTRL']) # Set RR
        time.sleep(0.001)
        return self.clearBit(PU_CTRL_Bits['NAU7802_PU_CTRL_RR'], Scale_Registers['NAU7802_PU_CTRL']) # Clear RR to leave reset state

    # Mask & set a given bit within a register
    def setBit(self, bitNumber, registerAddress):   
        value = self.getRegister(registerAddress)
        value |= (1 << bitNumber)    # Set this bit
        return self.setRegister(registerAddress, value)

    # Pass a known calibration factor into library. Helpful if users is loading settings from NVM.
    # If you don't know your cal factor, call setZeroOffset(), then calculateCalibrationFactor() with a known weight
    def setCalibrationFactor(self, newCalFactor):  
        self.calibrationFactor = newCalFactor

    # Select between 1 and 2
    def setChannel(self, channelNumber):
        if channelNumber == NAU7802_Channels['NAU7802_CHANNEL_1']:
            return self.clearBit(CTRL2_Bits['NAU7802_CTRL2_CHS'], Scale_Registers['NAU7802_CTRL2'])    # Channel 1 (default)
        else:
            return self.setBit(CTRL2_Bits['NAU7802_CTRL2_CHS'], Scale_Registers['NAU7802_CTRL2'])    # Channel 2

    # Set the gain
    # x1, 2, 4, 8, 16, 32, 64, 128 are avaialable
    def setGain(self, gainValue): 
        if gainValue > 0b111:
            gainValue = 0b111    # Error check

        value = self.getRegister(Scale_Registers['NAU7802_CTRL1'])
        value &= 0b11111000    # Clear gain bits
        value |= gainValue    # Mask in new bits

        return self.setRegister(Scale_Registers['NAU7802_CTRL1'], value)

    # Set Int pin to be high when data is ready (default)
    def setIntPolarityHigh(self):    # # Set Int pin to be high when data is ready (default)
        return self.clearBit(CTRL1_Bits['NAU7802_CTRL1_CRP'], Scale_Registers['NAU7802_CTRL1'])    # 0 = CRDY pin is high active (ready when 1)

    # Set Int pin to be low when data is ready
    def setIntPolarityLow(self):    # Set Int pin to be low when data is ready
        return self.setBit(CTRL1_Bits['NAU7802_CTRL1_CRP'], Scale_Registers['NAU7802_CTRL1'])    # 1 = CRDY pin is low active (ready when 0)

    # Set the onboard Low-Drop-Out voltage regulator to a given value
    # 2.4, 2.7, 3.0, 3.3, 3.6, 3.9, 4.2, 4.5V are available
    def setLDO(self, ldoValue):    # Set the onboard Low-Drop-Out voltage regulator to a given value. 2.4, 2.7, 3.0, 3.3, 3.6, 3.9, 4.2, 4.5V are avaialable
        if ldoValue > 0b111:
            ldoValue = 0b111    # Error check

        # Set the value of the LDO
        value = self.getRegister(Scale_Registers['NAU7802_CTRL1'])
        value &= 0b11000111    # Clear LDO bits
        value |= ldoValue << 3    # Mask in new LDO bits
        self.setRegister(Scale_Registers['NAU7802_CTRL1'], value)

        return self.setBit(PU_CTRL_Bits['NAU7802_PU_CTRL_AVDDS'], Scale_Registers['NAU7802_PU_CTRL'])    # Enable the internal LDO

    # Send a given value to be written to given address
    # Return true if successful
    def setRegister(self, registerAddress, value): 
        try:
            self.bus.write_word_data(self.deviceAddress, registerAddress, value)
        except:
            return False    # Sensor did not ACK
        return True

    # Set the readings per second
    # 10, 20, 40, 80, and 320 samples per second is available
    def setSampleRate(self, rate):  
        if rate > 0b111:
            rate = 0b111    # Error check

        value = self.getRegister(Scale_Registers['NAU7802_CTRL2'])
        value &= 0b10001111    # Clear CRS bits
        value |= rate << 4    # Mask in new CRS bits

        return self.setRegister(Scale_Registers['NAU7802_CTRL2'], value)

    # Sets the internal variable. Useful for users who are loading values from NVM.
    def setZeroOffset(self, newZeroOffset):
        self.zeroOffset = newZeroOffset 

    # Wait for asynchronous AFE calibration to complete with optional timeout.
    # If timeout is not specified (or set to 0), then wait indefinitely.
    # Returns true if calibration completes succsfully, otherwise returns false.
    def waitForCalibrateAFE(self, timeout = 0): 
        begin = time.time()
        cal_ready = 0

        while cal_ready == NAU7802_Cal_Status['NAU7802_CAL_IN_PROGRESS']:
            if (timeout > 0) and ((time.time() - begin) > timeout):
                break
            time.sleep(0.001)
            cal_ready = self.calAFEStatus()

        if cal_ready == NAU7802_Cal_Status['NAU7802_CAL_SUCCESS']:
            return True
        return False