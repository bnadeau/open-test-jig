import time

import ClydeUnitTest
import ClydeLog
import TestRig

class TestTouchyPowerOn(ClydeUnitTest.ClydeTestCase):
  def __init__(self, methodName):
    super(TestTouchyPowerOn, self).__init__(methodName)
    self.testRig = TestRig.rig

  #def setUp(self):

  def tearDown(self):
    self.testRig.disableRelay('HOST_VCC_3V3_LIMIT')
    self.testRig.disableRelay('HOST_VCC_5V_LIMIT')
    self.testRig.disableRelay('HOST_VCC_3V3')
    self.testRig.disableRelay('HOST_VCC_5V')
    self.testRig.disableRelay('HOST_GND')
      
  def test_010_off_current(self):
    MIN_OFF_CURRENT = 0
    MAX_OFF_CURRENT = 0
    
    self.testRig.enableRelay('HOST_GND')
    time.sleep(.5)
    
    current5V = self.testRig.current('5V')
    current3V3 = self.testRig.current('3V3')
    
    self.testRig.disableRelay('HOST_GND')

    self.log.info("Off 5V current: %0.2f <= %0.2f <= %0.2f." % (MIN_OFF_CURRENT, current5V, MAX_OFF_CURRENT))
    self.log.info("Off 3V3 current: %0.2f <= %0.2f <= %0.2f." % (MIN_OFF_CURRENT, current3V3, MAX_OFF_CURRENT))

    result = (current5V >= MIN_OFF_CURRENT and current5V <= MAX_OFF_CURRENT) and (current3V3 >= MIN_OFF_CURRENT and current3V3 <= MAX_OFF_CURRENT)
    self.assertTrue(result)
    
  def test_020_limited_current(self):
    MIN_5V_LIMITED_CURRENT = 0  #should not be zero. need to find way to detect low current.
    MAX_5V_LIMITED_CURRENT = 0
    MIN_3V3_LIMITED_CURRENT = 0
    MAX_3V3_LIMITED_CURRENT = 0
   
    self.testRig.enableRelay('HOST_GND')
    self.testRig.enableRelay('HOST_VCC_5V_LIMIT')
    self.testRig.enableRelay('HOST_VCC_3V3_LIMIT')
    time.sleep(.5)
    
    current5V = self.testRig.current('5V')
    current3V3 = self.testRig.current('3V3')
    
    self.testRig.disableRelay('HOST_VCC_3V3_LIMIT')
    self.testRig.disableRelay('HOST_VCC_5V_LIMIT')
    self.testRig.disableRelay('HOST_GND')
    
    self.log.info("Limited 5V current: %0.2f <= %0.2f <= %0.2f." % (MIN_5V_LIMITED_CURRENT, current5V, MAX_5V_LIMITED_CURRENT))
    self.log.info("Limited 3V3 current: %0.2f <= %0.2f <= %0.2f." % (MIN_3V3_LIMITED_CURRENT, current3V3, MAX_3V3_LIMITED_CURRENT))

    result = (current5V >= MIN_5V_LIMITED_CURRENT and current5V <= MAX_5V_LIMITED_CURRENT) and (current3V3 >= MIN_3V3_LIMITED_CURRENT and current3V3 <= MAX_3V3_LIMITED_CURRENT)
    self.assertTrue(result)