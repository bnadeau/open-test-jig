import unittest
import time
import traceback

import ClydeLog

class ClydeTestCase(unittest.TestCase):
  def __init__(self, methodName):
    super(ClydeTestCase, self).__init__(methodName)
    self.log = ClydeLog.getLogger()

  def run(self, result=None):
		if result.failures or result.errors:
			self.log.info(self.id() + " ABORTED")
		else:
			super(ClydeTestCase, self).run(result)

class ClydeTestRunner():
  def __init__(self, id):
    self.log = ClydeLog.getLogger()
    self.testid = id

  def run(self, name, test):
    self.log.info("START RUN: %s" % name)
    result = ClydeTestResult()
    startTime = time.time()
    test(result)
    stopTime = time.time()

    timeTaken = stopTime - startTime
    run = result.testsRun
    self.log.info("Ran %d test%s in %.3fs" % (run, run != 1 and "s" or "", timeTaken))
    if not result.wasSuccessful():
      failed, errored = map(len, (result.failures, result.errors))
      self.log.error("END RUN (failed: %d, errors: %d) TEST #%d\n" % (failed, errored, self.testid))
    else:
      self.log.success("END RUN: ALL OK! TEST #%d\n" % (self.testid))
    return result

class ClydeTestResult(unittest.TestResult):
  def __init__(self):
    unittest.TestResult.__init__(self)
    self.log = ClydeLog.getLogger()

  def startTest(self, test):
    unittest.TestResult.startTest(self, test)
    self.log.info(test.id().split('.')[-1] + " STARTED")

  def stopTest(self, test):
    self.log.info(test.id().split('.')[-1] + " STOP")
    #self.shouldStop = test.stopTests

  def addSuccess(self, test):
    unittest.TestResult.addSuccess(self, test)
    self.log.info(test.id().split('.')[-1] + " PASS")

  def addError(self, test, err):
    unittest.TestResult.addError(self, test, err)
    t, formatted_err = self.errors[-1]
    self.log.info(test.id().split('.')[-1] + " ERROR " + formatted_err.splitlines()[-1])

  def addFailure(self, test, err):
    unittest.TestResult.addFailure(self, test, err)
    t, formatted_err = self.failures[-1]
    self.log.info(test.id().split('.')[-1] + " FAILURE " + formatted_err.splitlines()[-1])
