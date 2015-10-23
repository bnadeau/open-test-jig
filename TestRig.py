import sys
import time

import DetectPlatform
import ClydeLog
import RemoteArduino

TEST_FIRMWARE_VERSION = 0.60

class ArduinoPin:
  def __init__(self, name, number, net = None, suppressHigh = False, suppressLow = False):
    self.name = name
    self.number = number

    if(net == None):
      self.net = name
    else:
      self.net = net

    self.suppressHigh = suppressHigh
    self.suppressLow = suppressLow

  def __str__(self):
    return self.name

class MeasurementPin():
  def __init__(self, name, number, multiplier, base):
    self.name = name
    self.number = number
    self.multiplier = multiplier
    self.base = base

  def __str__(self):
    return self.name
    
class TestRig:
  def __init__(self):
    self.log = ClydeLog.getLogger()
    self.board = None;
    self.measurementPins = []
    self.relayPins = []
    self.shortTestPins = []
    self.port = None
    self.ports = []

  def setPins(self, measurementPins, relayPins, shortTestPins):
    self.measurementPins = measurementPins
    self.relayPins = relayPins
    self.shortTestPins = shortTestPins  
    
  def connect(self, ports):
    serialPorts = DetectPlatform.ListSerialPorts()
    self.ports = ports
    self.port = None
    
    self.log.debug("Found %d serial ports:" % len(serialPorts))
    for serialPort in serialPorts:
      self.log.debug(" - " + serialPort)

    for port in ports:
      if serialPorts.count(port) > 0:
          self.port = port
          break
 
    if self.port != None:
      self.arduino = RemoteArduino.RemoteArduino(self.port)
    else:
      raise Exception("No Arduino found on port " + port)

    self.arduino.debug('OFF')

    arduinoVersion = self.arduino.version()
    if arduinoVersion < TEST_FIRMWARE_VERSION:
      self.log.debug("Remote version '%.2f' too low, upgrade the Arduino sketch" % arduinoVersion)
      sys.exit()
      
    self.board = self.arduino.getBoard()
    self.log.info("Found test rig: %s" % self.board);
    
    self.reset()
  
  def connectFirmware(self, ports):
    serialPorts = DetectPlatform.ListSerialPorts()
    self.ports = ports
    self.port = None
    
    self.log.debug("Found %d serial ports:" % len(serialPorts))
    for serialPort in serialPorts:
      self.log.debug(" - " + serialPort)

    for port in ports:
      if serialPorts.count(port) > 0:
          self.port = port
          break
 
    if self.port != None:
      self.arduino = RemoteArduino.RemoteArduino(self.port)
    else:
      raise Exception("No Arduino found on port " + port)
      
    self.board = 'CLYDE'
    self.log.info("Found board: %s" % self.board);
    
    self.reset()
      
  def disconnect(self):
    self.reset()
    self.arduino = None
    self.board = None
    
  def connected(self):
    return self.arduino is not None
    
  def disconnected(self):
    return self.arduino is None
    
  def reset(self):
    if self.board is 'CLYDE':
      return

    #""" Turn off LEDs. """
    self.arduino.led('GREEN', 'OFF');
    self.arduino.led('RED', 'OFF');
    self.arduino.led('WHITE', 'OFF');

    #""" Reset pins to default state. """
    # disable relays
    for pin in self.relayPins:
      self.arduino.relay(pin.number, 'OFF')

    # TODO
    # for pin in self.shortTestPins:
      # self.arduino.pinMode(pin.number, 'INPUT')

    # TODO: reset analog/measurement pins?
    
  def led(self, color, status):
    if self.board is not 'CLYDE':
      self.arduino.led(color, status)
  
  def enableRelay(self, relayName):
    """ Enable an output relay """
    for pin in self.relayPins:
      if pin.name == relayName:
        self.arduino.relay(pin.number, 'ON')
        return
    raise Exception("Relay " + relayName + " not found!")
    
  def disableRelay(self, relayName):
    """ Disable an output relay """
    for pin in self.relayPins:
      if pin.name == relayName:
        self.arduino.relay(pin.number, 'OFF')
        return
    raise Exception("Relay " + relayName + " not found!")

  def output(self, pinName, state):
    """ Set a digital pin to output LOW or HIGH """
    for pin in self.shortTestPins:
      if pin.name == pinName:
        self.arduino.pinMode(pin.number, 'OUTPUT')
        self.arduino.digitalWrite(pin.number, state)
        return
    raise Exception("Pin" + pinName + " not found!")

  def pwm(self, pinName, value):
    """ Set a digital pin to output a PWM value """
    for pin in self.shortTestPins:
      if pin.name == pinName:
        self.arduino.pinMode(pin.number, 'OUTPUT')
        self.arduino.analogWrite(pin.number, value)
        return
    raise Exception("Pin" + pinName + " not found!")
    
  def setInput(self, pinName):
    """ Set up a pin as input """
    for pin in self.shortTestPins:
      if pin.name == pinName:
        self.arduino.pinMode(pin.number, 'INPUT')
        return
    raise Exception("Pin" + pinName + "not found!")

  #def setInputPullup(self, pinName):
  #  """ Set up a pin as input in pullup mode """
  #  for pin in self.shortTestPins:
  #    if pin.name == pinName:
  #      self.arduino.pinMode(pin.number, 'INPUT_PULLUP')
  #      return
  #  raise Exception("Pin" + pinName + "not found!")

  #def readInput(self, pinName):
  #  """ Set up a pin as input in pullup mode """
  #  for pin in self.shortTestPins:
  #    if pin.name == pinName:
  #      return self.arduino.digitalRead(pin.number)
  #  raise Exception("Pin" + pinName + "not found!")

  def measure(self, measurementName):
    """ Read a measurement pin """
    for pin in self.measurementPins:
      if pin.name == measurementName:
        return pin.multiplier*(self.arduino.analogRead(pin.number) + pin.base)

    raise Exception("Measurement pin " + measurementName + " not found!")
    
  def current(self, voltage='5V'):
    """ Read current from current sensor """
    return self.arduino.current(voltage)
    
  def initMPR121(self, address):
    """ Initialize the MPR121 using default values """
    return self.arduino.initMPR121(address)
    
  def waitForTouch(self, address, pinName, timeout):
    """ Returns the touch states of the MPR121 as soon as a touch is detected, or until timeout. """
    for pin in self.shortTestPins:
      if pin.name == pinName:
        return self.arduino.waitForTouch(address, pin.number, timeout)
    raise Exception("Pin" + pinName + " not found!")
    
  def resetEEPROM(self):
    return self.arduino.resetEEPROM()
    
  def writeEEPROM(self, addr, value):
    return self.arduino.writeEEPROM(addr, value)
    
  def readEEPROM(self, addr):
    return self.arduino.readEEPROM(addr)

  def writeSerial(self, addr, serial):
    if len(serial) > 6:
      return False
      
    for c in serial:
      success = self.arduino.writeEEPROM(addr, ord(c))
      if success == False:
        return False
      addr += 1
    
    return True
    
  def readSerial(self, addr, length):
    serial = ""
    
    for i in xrange(0, length):
      serial += chr(self.arduino.readEEPROM(addr+i))
      
    return serial
    
  def idModule(self, dpinName, apinName):
    dpin = None;
    apin = None;
    for pin in self.shortTestPins:
      if pin.name == dpinName:
        dpin = pin.number
    for pin in self.measurementPins:
      if pin.name == apinName:
        apin = pin.number
    
    if apin == None:
      raise Exception("Pin" + apinName + " not found!")
    elif dpin == None:
      raise Exception("Pin" + dpinName + " not found!")
    else:
      return self.arduino.idModule(dpin, apin)
    
    

rig = TestRig();