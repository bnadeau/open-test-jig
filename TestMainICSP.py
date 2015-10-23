from subprocess import check_output
from subprocess import CalledProcessError

import ClydeUnitTest
import ClydeLog

class TestMainICSP(ClydeUnitTest.ClydeTestCase):
  def __init__(self, methodName):
    super(TestMainICSP, self).__init__(methodName)
    
  def test_010_pre_fuse_bits(self):
    success = False
  
    try:
      check_output(["avrdude", "-p", "m32u4", "-P", "usb", "-c", "avrispmkII", "-U", "lock:w:0x3f:m", "-e", "-B1"])
      success = True
    except CalledProcessError as e:
      #try again here with a slower -B2 or -B10
      try:
        output = check_output(["avrdude", "-p", "m32u4", "-P", "usb", "-c", "avrispmkII", "-U", "lock:w:0x3f:m", "-e", "-B2"])
        success = True
      except CalledProcessError as e:
        self.log.error("avrdude returned non-zero exit status %d" % e.returncode)
      except OSError as e:
        self.log.info("Test failed with error: %s" % e)
    except OSError as e:
        self.log.info("Test failed with error: %s" % e)
 
    self.assertTrue(success)

  def test_020_flash_test(self):
    success = False
  
    try:
      check_output(["avrdude", "-p", "m32u4", "-P", "usb", "-c", "avrispmkII", "-U", "flash:w:/home/pi/clyde/binary/Caterina-Clyde.hex", "-U", "flash:w:/home/pi/clyde/binary/ClydeTestRigFirmware.cpp.hex"])
      success = True
    except CalledProcessError as e:
      self.log.error("avrdude returned non-zero exit status %d" % e.returncode)
    except OSError as e:
        self.log.info("Test failed with error: %s" % e)
 
    self.assertTrue(success)
    
  def test_030_post_fuse_bits(self):
    success = False
  
    try:
      check_output(["avrdude", "-p", "m32u4", "-P", "usb", "-c", "avrispmkII", "-U", "lfuse:w:0xff:m", "-U", "hfuse:w:0xd0:m", "-U", "efuse:w:0xcb:m", "-U", "lock:w:0x2f:m"])
      success = True
    except CalledProcessError as e:
      self.log.error("avrdude returned non-zero exit status %d" % e.returncode)
    except OSError as e:
        self.log.info("Test failed with error: %s" % e)
 
    self.assertTrue(success)