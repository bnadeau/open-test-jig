from subprocess import check_output
from subprocess import CalledProcessError
import time

import ClydeUnitTest
import ClydeLog
import TestRig
import DetectPlatform

fo = open("serial", "r+")
lastSerial = fo.readline(6)
fo.close()

class TestMainFunctions(ClydeUnitTest.ClydeTestCase):
  def __init__(self, methodName):
    super(TestMainFunctions, self).__init__(methodName)
    self.testRig = TestRig.rig
       
  def setUp(self):
    if self.testRig.connected() and self.testRig.board is not 'CLYDE':
      self.testRig.pwm('WHITE_LIGHT', 255)
      self.testRig.pwm('RED_RGB', 0)
      self.testRig.pwm('GREEN_RGB', 0)
      self.testRig.pwm('BLUE_RGB', 0)

  """def tearDown(self):
    self.testRig.pwm('WHITE_LIGHT', 255)
    self.testRig.pwm('RED_RGB', 0)
    self.testRig.pwm('GREEN_RGB', 0)
    self.testRig.pwm('BLUE_RGB', 0)"""
        
  def test_010_white_light(self):
    self.testRig.pwm('WHITE_LIGHT', 0)
    success = self.ask_yes_no("Is the white light on? (Y/n) ")
    self.testRig.pwm('WHITE_LIGHT', 255)
    self.assertTrue(success)    
    
  def test_020_rgb_light(self):
    self.testRig.pwm('RED_RGB', 230)
    self.testRig.pwm('GREEN_RGB', 230)
    self.testRig.pwm('BLUE_RGB', 230)
    success = self.ask_yes_no("Are the RGB leds on and white? (Y/n) ")
    self.testRig.pwm('RED_RGB', 0)
    self.testRig.pwm('GREEN_RGB', 0)
    self.testRig.pwm('BLUE_RGB', 0)    
    self.assertTrue(success)
    
  def test_030_eye_jst(self):
    MIN_READING = 670
    MAX_READING = 675
 
    reading = self.testRig.measure('EYE_SIG')
 
    self.log.info("Eye reading: %0.2f <= %0.2f <= %0.2f." % (MIN_READING, reading, MAX_READING))

    result = reading >= MIN_READING and reading <= MAX_READING
    self.assertTrue(result)

  def test_040_module_one_id(self):
    MIN_ID = 1002
    MAX_ID = 1008
    
    #identify module
    reading = self.testRig.idModule('MODULE1_DIGITAL', 'MODULE1_ANALOG')
    
    self.log.info("Module 1 ID: %0.2f <= %0.2f <= %0.2f." % (MIN_ID, reading, MAX_ID))
    
    result = reading >= MIN_ID and reading <= MAX_ID
    self.assertTrue(result)

  def test_040_module_one_i2c(self):
    MPR121_ADDR = 0x5A
    
    success = self.testRig.initMPR121(MPR121_ADDR)
    
    self.log.info("Module 1 I2C: %s == %s" % (True, success))
    self.assertTrue(success)
    
  def test_050_module_two_id(self):
    #test the pins for AoD
    #note: this is not testing the 3V3 pin, and the I2C.
    #      version 2 of TF should have an address switch.
    #      we could use that to test.
    MIN_ID = 902
    MAX_ID = 918
    
    #identify module
    reading = self.testRig.idModule('MODULE2_DIGITAL', 'MODULE2_ANALOG')
    
    self.log.info("Module 2 ID: %0.2f <= %0.2f <= %0.2f." % (MIN_ID, reading, MAX_ID))
    
    result = reading >= MIN_ID and reading <= MAX_ID
    self.assertTrue(result)
    
  def test_051_module_two_sensor(self):
    #test the pins for AoD
    #note: this is not testing the 3V3 pin, and the I2C.
    #      version 2 of TF should have an address switch.
    #      we could use that to test.
    MIN_VALUE = 652
    MAX_VALUE = 662
      
    #read sensor
    self.testRig.setInput('MODULE2_DIGITAL')
    reading = self.testRig.measure('MODULE2_ANALOG')
    
    self.log.info("Module 2 sensor: %0.2f <= %0.2f <= %0.2f." % (MIN_VALUE, reading, MAX_VALUE))
    
    result = reading >= MIN_VALUE and reading <= MAX_VALUE
    self.assertTrue(result)
    
  def test_060_write_eeprom(self):
    success = False;
    
    success = self.testRig.resetEEPROM()
    
    successReset = self.testRig.resetEEPROM()
    
    self.log.info("Write EEPROM: %s == %s" % (True, success))
    self.assertTrue(success)
  
  def test_070_reset(self):
    success = False
    
    #disconnect test rig
    self.testRig.disconnect()

    #ask to press reset button
    print("Please press the RESET button...")
        
    #check for bootloader, which indicates that the board reset
    try:
      start = int(round(time.time() * 1000))
      while not success and (int(round(time.time() * 1000)) - start < 20000):
        output = check_output(["lsusb"])
        if "1d50:609e" in output:
          self.log.info("Found bootloader...")
          success = True
          break
        time.sleep(1)
    except CalledProcessError as e:
      self.log.error("lsusb returned non-zero exit status %d" % e.returncode)
      self.assertTrue(success)
      return
    except OSError as e:
      self.log.info("Test firmware flash failed with error: %s" % e)
      self.assertTrue(success)
      return
    
    self.log.info("Reset: %s == %s" % (True, success))
    self.assertTrue(success)
    
  def test_080_flash_firmware(self):
    success = False
  
    #identify port    
    serialPorts = DetectPlatform.ListSerialPorts()
    for p in self.testRig.ports:
      if serialPorts.count(p) > 0:
        port = p
        break
    
    #flash
    try:
      check_output(["avrdude", "-p", "m32u4", "-P", port, "-c", "avr109", "-b", "19200", "-U", "flash:w:/home/pi/clyde/binary/ClydeFirmware.cpp.hex"])
    except CalledProcessError as e:
      self.log.error("avrdude returned non-zero exit status %d" % e.returncode)
      self.assertTrue(success)
      return
    except OSError as e:
      self.log.info("Firmware flash failed with error: %s" % e)
      self.assertTrue(success)
      return
   
    #check that firmware started
    try:
      start = int(round(time.time() * 1000))
      while not success and (int(round(time.time() * 1000)) - start < 15000):
        print("checking for clyde...")
        output = check_output(["lsusb"])
        if "1d50:609f" in output:
          self.log.info("Found Clyde WOOT")
          success = True
          break
        time.sleep(1)
    except CalledProcessError as e:
      self.log.error("lsusb returned non-zero exit status %d" % e.returncode)
      self.assertTrue(success)
      return
    except OSError as e:
      self.log.info("Test failed with error: %s" % e)
      self.assertTrue(success)
      return
        
    time.sleep(2)
    self.testRig.connectFirmware(self.testRig.ports) 
       
    self.log.info("Firmware upload: %s == %s" % (True, success))
    self.assertTrue(success)
    
  def test_090_write_serial(self):
    global lastSerial
    SERIAL_ADDR = 0
    SERIAL_LENGTH = 6
    
    intSerial = int(lastSerial, 16)
    intSerial += 1
    nextSerial = format(intSerial, 'x').upper().zfill(6)

    success = self.testRig.writeSerial(SERIAL_ADDR, nextSerial)
    readSerial = self.testRig.readSerial(SERIAL_ADDR, SERIAL_LENGTH)
    
    self.log.info("Write serial: %s == %s" % (nextSerial, readSerial))
    self.assertTrue(success and (nextSerial == readSerial))
    
    if success and (nextSerial == readSerial):
      lastSerial = nextSerial
      fo = open("serial", "r+")
      fo.seek(0)
      fo.write(lastSerial)
      fo.truncate()
      fo.close()
    
  def test_100_write_qc(self):
    QC_EEPROM_ADDR = 6
    
    success = self.testRig.writeEEPROM(6, 1)
    readQC = self.testRig.readEEPROM(6)

    self.log.info("Write QC: %s == %s" % ('1', readQC))
    self.assertTrue(success and (readQC == 1))
    
  def ask_yes_no(self, prompt):
    while True:
      s = raw_input(prompt)
      if set(s).issubset("ynYNqQ") or s == "":
        return s == 'Y' or s == 'y' or s == ''
      print("Please answer 'y' for yes, or 'n' for no.")
    