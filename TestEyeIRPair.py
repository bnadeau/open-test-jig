import time
import math

import ClydeUnitTest
import ClydeLog
import TestRig

class TestEyeIRPair(ClydeUnitTest.ClydeTestCase):
  def __init__(self, methodName):
    super(TestEyeIRPair, self).__init__(methodName)
    self.testRig = TestRig.rig

  def test_010_full_current(self):
    MIN_OPERATING_CURRENT = 36
    MAX_OPERATING_CURRENT = 46
 
    self.testRig.enableRelay('HOST_GND')
    self.testRig.enableRelay('DUT_SIG')
    self.testRig.enableRelay('HOST_VCC')
    time.sleep(.5)

    current = self.testRig.current()

    self.testRig.disableRelay('HOST_VCC')
    self.testRig.disableRelay('DUT_SIG')
    self.testRig.disableRelay('HOST_GND')
    
    self.log.info("Full current: %0.2f <= %0.2f <= %0.2f." % (MIN_OPERATING_CURRENT, current, MAX_OPERATING_CURRENT))

    result = current >= MIN_OPERATING_CURRENT and current <= MAX_OPERATING_CURRENT
    self.assertTrue(result)
    
  def test_020_base_ir(self):
    MIN_VOLTAGE = 20
    MAX_VOLTAGE = 50
    MAX_DIFF = 20
 
    self.testRig.enableRelay('HOST_GND')
    self.testRig.enableRelay('HOST_VCC')
    self.testRig.enableRelay('DUT_SIG')
    time.sleep(1)

    voltage_one = self.testRig.measure('DUT_SIG')

    self.log.info("Base IR voltage (first pass): %0.2f <= %0.2f <= %0.2f." % (MIN_VOLTAGE, voltage_one, MAX_VOLTAGE))
    result_one = voltage_one >= MIN_VOLTAGE and voltage_one <= MAX_VOLTAGE
    
    time.sleep(1)

    voltage_two = self.testRig.measure('DUT_SIG')

    self.testRig.disableRelay('DUT_SIG')
    self.testRig.disableRelay('HOST_VCC')
    self.testRig.disableRelay('HOST_GND')

    self.log.info("Base IR voltage (second pass): %0.2f <= %0.2f <= %0.2f." % (MIN_VOLTAGE, voltage_two, MAX_VOLTAGE))
    result_two = voltage_two >= MIN_VOLTAGE and voltage_two <= MAX_VOLTAGE    

    self.log.info("Base IR voltage difference: 0 <= %0.2f <= %0.2f." % (math.fabs(voltage_two-voltage_one), MAX_DIFF))
    
    result_diff = math.fabs(voltage_two-voltage_one) < MAX_DIFF
    
    self.assertTrue(result_one & result_two & result_diff)