import time

import ClydeUnitTest
import ClydeLog
import TestRig

class TestEyePowerOn(ClydeUnitTest.ClydeTestCase):
  def __init__(self, methodName):
    super(TestEyePowerOn, self).__init__(methodName)
    self.testRig = TestRig.rig
    
  def test_010_off_current(self):
    MIN_OFF_CURRENT = 0
    MAX_OFF_CURRENT = 0
    
    self.testRig.enableRelay('HOST_GND')
    time.sleep(.5)
    
    current = self.testRig.current()
    
    self.testRig.disableRelay('HOST_GND')

    self.log.info("Off current: %0.2f <= %0.2f <= %0.2f." % (MIN_OFF_CURRENT, current, MAX_OFF_CURRENT))

    result = current >= MIN_OFF_CURRENT and current <= MAX_OFF_CURRENT
    self.assertTrue(result)
    
  def test_020_limited_current(self):
    MIN_LIMITED_CURRENT = 26
    MAX_LIMITED_CURRENT = 35
   
    self.testRig.enableRelay('HOST_GND')
    self.testRig.enableRelay('HOST_VCC_LIMIT')
    time.sleep(.5)
    
    current = self.testRig.current()
    
    self.testRig.disableRelay('HOST_VCC_LIMIT')
    self.testRig.disableRelay('HOST_GND')
    
    self.log.info("Limited current: %0.2f <= %0.2f <= %0.2f." % (MIN_LIMITED_CURRENT, current, MAX_LIMITED_CURRENT))

    if (current == 0):
      self.log.warning("Detected no current. Make sure that rig lever is down, and PCB is placed correctly.")
    
    result = current >= MIN_LIMITED_CURRENT and current <= MAX_LIMITED_CURRENT
    self.assertTrue(result)