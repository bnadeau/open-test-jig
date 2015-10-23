import serial
import time
from decimal import *

EOR = ''.join([chr(13), chr(10)])

class RemoteArduino:
  """ Class to control an Arduino remotely. A light Firmata-like thing. """
  def __init__(self, port):
    """ Open a connection to an arduino
    port: Serial port device name, for example: '/dev/ttyACM0'
    """
    self.serial = serial.Serial(port, baudrate=19200, timeout=10.0)

  def sendCommand(self, command, args=None):
    if (args is not None):
      command += ' ' + args;
      
    self.serial.write(command)
    self.serial.write(EOR)

    response = self.serial.readline()

    #make sure we have a complete response
    if (not response.endswith(EOR)):
      raise Exception("Bad response for command '%s'. End of response not found. Timed out." % command)
    
    #clean up
    response = response.rstrip(EOR)
    tokens = response.split()

    #make sure that the response starts with OK or ERR
    try:
      if (tokens[0] not in {'OK', 'ERR'}):
        raise Exception("Bad response for command '%s'. Response starts with '%s' and not OK or ERR." % (command, tokens[0]))    
    except IndexError:
      raise Exception("Bad response for command '%s'. Response is empty." % command)
      
    #check if the response is an error
    try:
      if (tokens[0] == 'ERR'):
        raise Exception("Error response '%s' for command '%s'" % (tokens[1], command))      
    except IndexError:
      raise Exception("Bad response for command '%s'. Missing error code." % command)
    
    tokens.pop(0)
    return tokens

  def version(self):
    """ Read the arduino sketch version. """
    response = self.sendCommand('VERSION')
    
    try:
      value = Decimal(response[0])
      value = float(value)
    except ValueError:
      raise Exception("Bad response for command '%s'. Version '%s' is not a number." % ('VERSION', response[0]))
    except IndexError:
      raise Exception("Bad response for command '%s'. Missing value." % 'VERSION')
    
    return value
    
  def setBoard(self, board):
    """ Configure the Arduino to test a specific type of board. """
    response = self.sendCommand('SET_BOARD', board)
    
    try:
      if (response[0] != board):
        raise Exception("Bad response for command '%s'. Failed to set board %s. Response value is '%s'." % ('SET_BOARD', board, response[0]))
    except IndexError:
      raise Exception("Bad response for command '%s'. Missing value." % 'SET_BOARD')
    
    return True
    
  def getBoard(self):
    """ Get the type of board the Arduino is configured to test. """
    response = self.sendCommand('GET_BOARD')
    
    try:
      board = response[0]
    except IndexError:
      raise Exception("Bad response for command '%s'. Missing value." % 'GET_BOARD')
    
    return board
    
  def led(self, color, status):
    """ Enable or disable a relay on the specified pin. """
    self.sendCommand('LED', ' '.join([color, status]))
    return True
  
  def relay(self, pin, status):
    """ Enable or disable a relay on the specified pin. """
    self.sendCommand('RELAY', ' '.join([str(pin), status]))
    return True
  
  def current(self, voltage='5V'):
    """ Read the current from the shield's current sensor. """
    response = self.sendCommand('READ_CURRENT', voltage)
    
    try:
      value = Decimal(response[0])
      value = float(value)
    except ValueError:
      raise Exception("Bad response for command '%s'. Value '%s' is not a float." % ('READ_CURRENT', response[0]))
    except IndexError:
      raise Exception("Bad response for command '%s'. Missing value." % 'READ_CURRENT')
    
    return value

  def pinMode(self, pin, mode):
    """ Change the mode of a digital pin. """
    self.sendCommand('PIN_MODE', ' '.join(['DIGITAL', str(pin), mode]))

  def analogWrite(self, pin, value):
    """ Change the state of a digital pin configured as output. """
    self.sendCommand('WRITE_ANALOG', ' '.join([str(pin), str(value)]))

  def digitalWrite(self, pin, value):
    """ Change the state of a digital pin configured as output. """
    self.sendCommand('WRITE_DIGITAL', ' '.join([str(pin), value]))
    
  def analogRead(self, pin):
    """ Read the value of an analog pin. """
    response = self.sendCommand('READ_ANALOG', str(pin))
    
    try:
      value = int(response[0])
    except ValueError:
      raise Exception("Bad response for command '%s %s'. Value '%s' is not an integer." % ('READ_ANALOG', str(pin), response[0]))
    except IndexError:
      raise Exception("Bad response for command '%s'. Missing value." % 'READ_ANALOG')
    
    return value

  def digitalRead(self, pin):
    """ Read the value of a digital pin. """
    response = self.sendCommand('READ_DIGITAL', str(pin))
    
    try:
      if (response[0] in {'0', '1'}):
        value = int(response[0])
      else:
        raise Exception("Bad response for command '%s %s'. Value '%s' is not 0 or 1." % ('READ_DIGITAL', str(pin), response[0]))
    except ValueError:
      raise Exception("Bad response for command '%s %s'. Value '%s' is not an integer." % ('READ_DIGITAL', str(pin), response[0]))
    except IndexError:
      raise Exception("Bad response for command '%s'. Missing value." % 'READ_ANALOG')
    
    return value

  def debug(self, status):
    """ Enable/disable debug mode. """
    self.sendCommand('DEBUG', status)
    return True
    
  def initMPR121(self, address):
    """ Initializes an MPR121 at the given address.
        Returns OK on success, FAILED otherwise. """
    self.sendCommand('INIT_MPR121', str(address))
    return True
    
  def waitForTouch(self, address, pin, timeout):
    """ Get the touch status of the MPR121 at the given address.
        Waits for a touch until timeout.
        Returns empty touch status if timeout is reached. """
    response = self.sendCommand('WAIT_TOUCH', ' '.join([str(address), str(pin), str(timeout)]))

    try:
      value = int(response[0])
    except ValueError:
      raise Exception("Bad response for command '%s %s %s %s'. Value '%s' is not an integer." % ('WAIT_TOUCH', str(addr), str(pin), str(timeout), response[0]))
    except IndexError:
      raise Exception("Bad response for command '%s'. Missing value." % 'WAIT_TOUCH')
    
    return value
  
  def resetEEPROM(self):
    self.sendCommand('RESET_EEPROM')
    return True
    
  def writeEEPROM(self, addr, value):
    self.sendCommand('WRITE_EEPROM', ' '.join([str(addr), str(value)]))
    return True
    
  def readEEPROM(self, addr):
    response = self.sendCommand('READ_EEPROM', str(addr))

    try:
      value = int(response[0])
    except ValueError:
      raise Exception("Bad response for command '%s %s'. Value '%s' is not an integer." % ('WAIT_TOUCH', str(addr), response[0]))
    except IndexError:
      raise Exception("Bad response for command '%s'. Missing value." % 'WAIT_TOUCH')
    
    return value
    
  def idModule(self, dpin, apin):
    response = self.sendCommand('ID_MODULE', ' '.join([str(dpin), str(apin)]))
    
    try:
      value = int(response[0])
    except ValueError:
      raise Exception("Bad response for command '%s %s %s'. Value '%s' is not an integer." % ('ID_MODULE', str(dpin), str(apin), response[0]))
    except IndexError:
      raise Exception("Bad response for command '%s'. Missing value." % 'ID_MODULE')
    
    return value

