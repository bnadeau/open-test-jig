import subprocess
import time
import glob

def detectPlatform():
  data = []
  proc = subprocess.Popen(["uname"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)

  while True:
    read = proc.stdout.readline() #block / wait
    if not read:
        break
    data.append(read)
    
  if 'Linux' in data[0]:
    return "Linux"

  return "Unknown"

def ListSerialPorts():
  # Scan for all connected devices; platform dependent
  platform = detectPlatform()

  ports = []
  if platform == 'Linux':
    ports.extend(glob.glob("/dev/ttyACM*"))
    ports.extend(glob.glob("/dev/ttyUSB*"))

  return ports
