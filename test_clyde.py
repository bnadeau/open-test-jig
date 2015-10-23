import menusystem
import unittest
import os
import sys
import time

from subprocess import check_output
from subprocess import CalledProcessError

import ClydeLog
import ClydeUnitTest
import TestRig

RIG_PORT = ['/dev/ttyACM0', '/dev/ttyACM1']

testid = 0

# Handler functions
def run_test_session(names, board):
  print("")
  input = get_input("Do you want to run the first test? (Y/n) ")
  next = input == 'y' or input == 'Y' or input == ''
  print("")
  while next:
    run_tests(names, board)
    input = get_input("Do you want to run the next test? (Y/n) ")
    next = input == 'y' or input == 'Y' or input == ''
    print("")

def run_main_test_session(first_names, second_names, board):
  setMainPins()
  #loadSerial()
  print("Found test rig: %s" % 'MAIN');
  #print("Last serial: %s" % lastSerial);
  input = get_input("Do you want to run the first test? (Y/n) ")
  next = input == 'y' or input == 'Y' or input == ''
  print("")
  while next:
    run_main_tests(first_names, second_names, board)
    input = get_input("Do you want to run the next test? (Y/n) ")
    next = input == 'y' or input == 'Y' or input == ''
    print("")
    
def get_input(prompt):
  while True:
    s = raw_input(prompt)
    if set(s).issubset("ynYNqQ") or s == "":
      return s
    print("Please answer 'y' for yes, or 'n' for no.")
    
def run_tests(names, board):
  global testid
  
  names = names.split();

  if (TestRig.rig.board is not None):
    TestRig.rig.reset();
    
  allTests = unittest.TestSuite()
  
  for name in names:
    module = __import__(name)
    tests = unittest.defaultTestLoader.loadTestsFromModule(module)
    allTests.addTests(tests)
  
  testid += 1
  runner = ClydeUnitTest.ClydeTestRunner(testid)
  result = runner.run(board, allTests)
  
  if (TestRig.rig.board is not None):
    TestRig.rig.reset()
    TestRig.rig.led('GREEN' if result.wasSuccessful() else 'RED', 'ON')

def run_main_tests(first_names, second_names, board):
  global testid
  
  #first set of tests
  first_names = first_names.split();
    
  allTests = unittest.TestSuite()
  
  for name in first_names:
    module = __import__(name)
    tests = unittest.defaultTestLoader.loadTestsFromModule(module)
    allTests.addTests(tests)
    
  testid += 1 
  runner = ClydeUnitTest.ClydeTestRunner(testid)
  result = runner.run(board, allTests)
 
  if not result.wasSuccessful():
    if TestRig.rig.board is not None:
      TestRig.rig.reset()
      TestRig.rig.led('RED', 'ON')
    return
  
  start = int(round(time.time() * 1000))
  found = False
  timeout = 15000.0
  while not found and (int(round(time.time() * 1000)) - start < timeout):
    sys.stdout.write("\rLoading [ %.3fs ]" % (int(int(round(time.time() * 1000)) - start) / 1000.0))
    sys.stdout.flush()
    output = check_output(["lsusb"])
    if "1d50:609f" in output:
      found = True
    time.sleep(1)
  
  sys.stdout.write("\n\n")
  
  time.sleep(2)
  TestRig.rig.connect(RIG_PORT)

  #second set of tests
  second_names = second_names.split();

  if (TestRig.rig.board is not None):
    TestRig.rig.reset();
    
  allTests = unittest.TestSuite()
  
  for name in second_names:
    module = __import__(name)
    tests = unittest.defaultTestLoader.loadTestsFromModule(module)
    allTests.addTests(tests)
  
  runner = ClydeUnitTest.ClydeTestRunner(testid)
  result = runner.run(board, allTests)

  if (TestRig.rig.board is not None):
    TestRig.rig.reset()
    TestRig.rig.led('GREEN' if result.wasSuccessful() else 'RED', 'ON')
    
def done(value):
  if (TestRig.rig is not None):
    TestRig.rig.disconnect()
    TestRig.rig = None
  return False
  
def setMainPins():
  # List of pins that are connected to analog sensors on the board
  measurementPins = [
    TestRig.MeasurementPin('EYE_SIG', 0, 1, 0), # this could do 1/1023 * v + 0 to convert to 0-5V
    TestRig.MeasurementPin('MODULE1_ANALOG', 1, 1, 0),
    TestRig.MeasurementPin('MODULE2_ANALOG', 2, 1, 0),
    ]

  # List of pins that control a relay on the test rig
  relayPins = [
    ]
  
  # List of pins that are connected directly to an I/O pin on the DUT,
  # that should be used to do an n*n short test
  # For nodes with reverse protection diodes (eg, VCC and GND), specifcy
  # 'suppressHigh' to prevent them from being pulled higher than any other
  # nets, and 'suppressLow' to prevent them from being pulled lower than any
  # other nets.
  shortTestPins = [
    TestRig.ArduinoPin('WHITE_LIGHT', 11),
    TestRig.ArduinoPin('RED_RGB', 5),
    TestRig.ArduinoPin('GREEN_RGB', 6),
    TestRig.ArduinoPin('BLUE_RGB', 9),
    TestRig.ArduinoPin('MODULE1_DIGITAL', 7),
    TestRig.ArduinoPin('MODULE2_DIGITAL', 8),
    ]  
    
  return TestRig.rig.setPins(measurementPins, relayPins, shortTestPins)
  
def setEyePins():
  # List of pins that are connected to analog sensors on the board
  measurementPins = [
    TestRig.MeasurementPin('DUT_SIG', 0, 1, 0), # this could do 1/1023 * v + 0 to convert to 0-5V
    ]

  # List of pins that control a relay on the test rig
  relayPins = [
    TestRig.ArduinoPin('HOST_VCC_LIMIT', 5),
    TestRig.ArduinoPin('HOST_VCC',       6),
    TestRig.ArduinoPin('HOST_GND',       8),
    TestRig.ArduinoPin('DUT_SIG',        7),
    ]
  
  # List of pins that are connected directly to an I/O pin on the DUT,
  # that should be used to do an n*n short test
  # For nodes with reverse protection diodes (eg, VCC and GND), specifcy
  # 'suppressHigh' to prevent them from being pulled higher than any other
  # nets, and 'suppressLow' to prevent them from being pulled lower than any
  # other nets.
  shortTestPins = [
    ]  
    
  return TestRig.rig.setPins(measurementPins, relayPins, shortTestPins)
	
def setModulePins():
  # List of pins that are connected to analog sensors on the board
  measurementPins = [
    TestRig.MeasurementPin('DUT_ANALOG', 0, 1, 0), # this could do 1/1023 * v + 0 to convert to 0-5V
    ]

  # List of pins that control a relay on the test rig
  relayPins = [
    TestRig.ArduinoPin('HOST_VCC_5V_LIMIT',  5),
    TestRig.ArduinoPin('HOST_VCC_5V',        6),
    TestRig.ArduinoPin('HOST_VCC_3V3_LIMIT', 13), #changing to analog 1 / digital 15 (A1)
    TestRig.ArduinoPin('HOST_VCC_3V3',       4),
    TestRig.ArduinoPin('HOST_GND',           7),
    ]
  
  # List of pins that are connected directly to an I/O pin on the DUT,
  # that should be used to do an n*n short test
  # For nodes with reverse protection diodes (eg, VCC and GND), specify
  # 'suppressHigh' to prevent them from being pulled higher than any other
  # nets, and 'suppressLow' to prevent them from being pulled lower than any
  # other nets.
  shortTestPins = [
    TestRig.ArduinoPin('DUT_DIGITAL', 11),
    ]  
    
  return TestRig.rig.setPins(measurementPins, relayPins, shortTestPins)

if __name__ == '__main__':
  # Check if we are testing the main board
  if len(sys.argv) > 1 and sys.argv[1] == 'MAIN':
    run_main_test_session('TestMainICSP', 'TestMainFunctions', 'MAIN')
  else:
    # Connect test rig
    TestRig.rig.connect(RIG_PORT)

    if TestRig.rig.board == 'EYE':
      setEyePins()
      run_test_session('TestEyePowerOn TestEyeIRPair', TestRig.rig.board)
    elif TestRig.rig.board == 'TOUCH':
      setModulePins()
      run_test_session('TestTouchyPowerOn TestTouchyFunctions', TestRig.rig.board)
    elif TestRig.rig.board == 'AFRAID':
      setModulePins()
      run_test_session('TestAfraidPowerOn TestAfraidFunctions', TestRig.rig.board)
    elif TestRig.rig.board == 'MAIN':
      run_test_session('', TestRig.rig.board);
    else:
      # Create main Clyde test menu
      menu_choices = []
      menu_choices.append(menusystem.Choice(selector=1, value=1, handler=None, description='PCB000001-A: Test Main controller board'))
      menu_choices.append(menusystem.Choice(selector=2, value='TestEyePowerOn TestEyeIRPair', handler=test_eye, description='PCB000002-A: Test Eye IR board'))
      menu_choices.append(menusystem.Choice(selector=3, value='TestTouchyPowerOn TestTouchyFunctions', handler=test_touchy, description='PCB000003-A: Test Touchy-Feely module board'))
      menu_choices.append(menusystem.Choice(selector=4, value='TestAfraidPowerOn TestAfraidFunctions', handler=test_afraid, description='PCB000004-A: Test Afraid of the Dark module board'))
      menu_choices.append(menusystem.Choice(selector='q', value=0, handler=done, description='Quit'))

      menu = menusystem.Menu(title='Clyde Tests', choice_list=menu_choices, prompt='Press 1-4 to select the type of PCB under test. Press \'q\' to quit. ')

      menu.waitForInput()