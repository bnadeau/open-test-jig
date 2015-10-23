import time
import math

import ClydeUnitTest
import ClydeLog
import TestRig

class TestTouchyFunctions(ClydeUnitTest.ClydeTestCase):
  def __init__(self, methodName):
    super(TestTouchyFunctions, self).__init__(methodName)
    self.testRig = TestRig.rig

  #def setUp(self):

  def tearDown(self):
    self.testRig.disableRelay('HOST_VCC_3V3_LIMIT')
    self.testRig.disableRelay('HOST_VCC_5V_LIMIT')
    self.testRig.disableRelay('HOST_VCC_3V3')
    self.testRig.disableRelay('HOST_VCC_5V')
    self.testRig.disableRelay('HOST_GND')
    
  """def test_010_full_current(self):
    MIN_5V_OPERATING_CURRENT = 0 #should not be zero or 1 to 3. need to find way to detect low current.
    MAX_5V_OPERATING_CURRENT = 0
    MIN_3V3_OPERATING_CURRENT = 0
    MAX_3V3_OPERATING_CURRENT = 3
 
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
    MIN_VOLTAGE = 1001
    MAX_VOLTAGE = 1007
 
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
    
  def test_030_mpr121(self):
    NUM_ELECTRODES = 6
    MPR121_ADDR = 0x5A
  
    self.testRig.enableRelay('HOST_GND')
    self.testRig.enableRelay('HOST_VCC_5V')
    self.testRig.enableRelay('HOST_VCC_3V3')
    time.sleep(.5)
  
    response = self.testRig.initMPR121(MPR121_ADDR);
    time.sleep(5)
    passed = self.check_electrodes(MPR121_ADDR, NUM_ELECTRODES)
  
    self.testRig.disableRelay('HOST_VCC_3V3')
    self.testRig.disableRelay('HOST_VCC_5V')
    self.testRig.disableRelay('HOST_GND')
    
    self.log.info("MPR121 initialization: OK")
    self.log.info("MPR121 electrodes: %d of %d." % (passed, NUM_ELECTRODES))
    result = passed >= NUM_ELECTRODES/2
    self.assertTrue(result)
    
  def check_electrodes(self, addr, numElectrodes):
    totalResult = 0
    totalCount = 0
    
    totalGoal = 0
    for electrode in xrange(0, numElectrodes):
      totalGoal |= 1 << electrode

    self.log.info("Touch the %d legs one by one..." % (numElectrodes))
    self.log.info("[%s]" % (bin(totalResult)[2:].zfill(numElectrodes)));
    
    timeout = time.time() + 30   # 30 seconds
    while totalCount < numElectrodes/2 and time.time() < timeout:
      #wait for touch
      result = self.testRig.waitForTouch(addr, 'DUT_DIGITAL', 8000)
      result = result & totalGoal;
      
      if self.is_power2(result):
        if (totalResult & result) == 0:
          totalResult |= result
          totalCount += 1
        else:
          self.log.info("Repeated touch detected. (%s)" % (bin(result)[2:].zfill(numElectrodes)[::-1]));
      else:
        self.log.info("More than one touch detected. (%s)" % (bin(result)[2:].zfill(numElectrodes)[::-1]));
        
      self.log.info("[%s]" % (bin(totalResult)[2:].zfill(numElectrodes)[::-1]));
        
    return totalCount
  
  def is_power2(self, num):
    return num > 0 and (num & (num - 1)) == 0
