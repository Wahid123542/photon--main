def validIndex(val: int, len: int):
  return val>=0 and val<len

from configparser import ConfigParser

def readConfig(filename, section):
  parser=ConfigParser()
  parser.read(filename)

  res={}
  if parser.has_section(section):
    params=parser.items(section)
    for p in params:
      res[p[0]]=p[1]
  else:
    raise Exception('Section {0} not found in the {1} file'.format(section, filename))
  
  return res

import os

def isDevMode():
  return os.getenv("APP_MODE")=="DEV" # <- NORMAL MODE UNCOMMENT
  #return True  # <- DEV MODE UNCOMMENT
