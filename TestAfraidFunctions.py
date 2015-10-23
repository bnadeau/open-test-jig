import time
import math

import ClydeUnitTest
import ClydeLog
import TestRig

class TestTouchyFunctions(ClydeUnitTest.ClydeTestCase):
  def __init__(self, methodName):
    super(TestTouchyFunctions, self).__init__(methodName)
    self.testRig = TestRig.rig
    self.mpr121Address = 0x5A

  #def setUp(self):

  def tearDown(self):
    self.testRig.disableRelay('HOST_VCC_3V3_LIMIT')
    self.testRig.disableRelay('HOST_VCC_5V_LIMIT')
    self.testRig.disableRelay('HOST_VCC_3V3')
    self.testRig.disableRelay('HOST_VCC_5V')
    self.testRig.disableRelay('HOST_GND')
    
  """def test_010_full_current(self):
    MIN_5V_OPERATING_CURRENT = 36 #TMP
    MAX_5V_OPERATING_CURRENT = 46 #TMP
    MIN_3V3_OPERATING_CURRENT = 36 #TMP
    MAX_3V3_OPERATING_CURRENT = 46 #TMP
 
    self.testRig.enableRelay('HOST_GND')
    self.testRig.enableRelay('HOST_VCC_5V')
    self.testRig.enableRelay('HOST_VCC_3V3')
    time.sleep(.5)
       
    current5V = self.testRig.current('5V')
    current3V3 = self.testRig.current('3V3')

    self.testRig.disableRelay('HOST_VCC_3V3')
    self.testRig.disableRelay('HOST_VCC_5V')
    self.testRig.disableRelay('HOST_GND')
    
    self.log.info("Full 5V current: %0.2f <= %0.2f <= %0.2f." % (MIN_5V_OPERATING_CURRENT, current5V, MAX_5V_OPERATING_CURRENT))
    self.log.info("Full 3V3 current: %0.2f <= %0.2f <= %0.2f." % (MIN_3V3_OPERATING_CURRENT, current3V3, MAX_3V3_OPERATING_CURRENT))

    result = (current5V >= MIN_5V_OPERATING_CURRENT and current5V <= MAX_5V_OPERATING_CURRENT) and (current3V3 >= MIN_3V3_OPERATING_CURRENT and current3V3 <= MAX_3V3_OPERATING_CURRENT)
    self.assertTrue(result)"""
    
  def test_020_module_id(self):
    MIN_VOLTAGE = 901
    MAX_VOLTAGE = 905
 
    self.testRig.enableRelay('HOST_GND')
    self.testRig.enableRelay('HOST_VCC_5V')
    self.testRig.enableRelay('HOST_VCC_3V3')
    time.sleep(.5)

    #activate ID circuit with digital pin
    voltage = self.testRig.idModule('DUT_DIGITAL', 'DUT_ANALOG')
        
    self.testRig.disableRelay('HOST_VCC_3V3')
    self.testRig.disableRelay('HOST_VCC_5V')
    self.testRig.disableRelay('HOST_GND')

    self.log.info("Module ID voltage: %0.2f <= %0.2f <= %0.2f." % (MIN_VOLTAGE, voltage, MAX_VOLTAGE))
    result = voltage >= MIN_VOLTAGE and voltage <= MAX_VOLTAGE
    
    self.assertTrue(result)
    
  def test_030_light_sensor(self):
    MIN_VOLTAGE = 50
    MAX_VOLTAGE = 250
  
    self.testRig.enableRelay('HOST_GND')
    self.testRig.enableRelay('HOST_VCC_5V')
    self.testRig.enableRelay('HOST_VCC_3V3')
    time.sleep(.5)
    
    self.testRig.led('WHITE', 'ON')
    time.sleep(.5)
  
    voltage = self.testRig.measure('DUT_ANALOG')
    self.testRig.led('WHITE', 'OFF')
  
    self.testRig.disableRelay('HOST_VCC_3V3')
    self.testRig.disableRelay('HOST_VCC_5V')
    self.testRig.disableRelay('HOST_GND')
    
    self.log.info("Light sensor voltage: %0.2f <= %0.2f <= %0.2f." % (MIN_VOLTAGE, voltage, MAX_VOLTAGE))
    result = voltage >= MIN_VOLTAGE and voltage <= MAX_VOLTAGE
    
    self.assertTrue(result)
