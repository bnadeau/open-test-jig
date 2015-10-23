import logging
import time
import os

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

format = "%(asctime)s %(levelname)-10s %(message)s"
id = time.strftime("%Y%m%d-%H%M%S")

#These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

def formatter_message(message, use_color = True):
  if use_color:
    message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
  else:
    message = message.replace("$RESET", "").replace("$BOLD", "")
  return message

COLORS = {
    'WARNING': YELLOW,
    'INFO': WHITE,
    'DEBUG': BLUE,
    'CRITICAL': YELLOW,
    'ERROR': RED,
    'PASS': GREEN
}

class ColoredFormatter(logging.Formatter):
  def __init__(self, msg, use_color = True):
    logging.Formatter.__init__(self, msg)
    self.use_color = use_color

  def format(self, record):
    levelname = record.levelname
    if self.use_color and levelname in COLORS:
      levelname_color = COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
      record.levelname = levelname_color
    return logging.Formatter.format(self, record)

    
PASS_LEVEL_NUM = 45
logging.addLevelName(PASS_LEVEL_NUM, 'PASS')
def success(self, message, *args, **kws):
    # Yes, logger takes its '*args' as 'args'.
    self._log(PASS_LEVEL_NUM, message, args, **kws) 
logging.Logger.success = success    
    
def getLogger(name = 'clyde_log'):
  return logging.getLogger();

log = getLogger()
log.setLevel(logging.DEBUG)

# Make sure log directory exists
if not os.path.exists('log'):
  os.makedirs('log')
    
# Log to file
formatter = logging.Formatter(format)
filehandler = logging.FileHandler("log/clyde_%s.log" % id, "w")
filehandler.setLevel(logging.INFO)
filehandler.setFormatter(formatter)
log.addHandler(filehandler)

COLOR_FORMAT = formatter_message(format, True)
color_formatter = ColoredFormatter(COLOR_FORMAT)

# Log to stdout too
streamhandler = logging.StreamHandler()
streamhandler.setLevel(logging.DEBUG)
streamhandler.setFormatter(color_formatter)
log.addHandler(streamhandler)
