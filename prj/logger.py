#!/usr/bin/env python

import logging
import logging.handlers as handlers
import time

def GetLogger(app, logFile):
  logger = logging.getLogger(app)
  logger.setLevel(logging.INFO)
  logHandler = handlers.RotatingFileHandler(logFile, maxBytes=1024*1024, backupCount=2)
  formatter = logging.Formatter(
    '%(asctime)s %(name)s %(levelname)s [%(process)d]: %(message)s',
    '%b %d %H:%M:%S')
  logHandler.setFormatter(formatter)
  logger.addHandler(logHandler)
  return logger
