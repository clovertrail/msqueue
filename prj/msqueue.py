#!/usr/bin/env python

import persistqueue
import time

import azureutils
import constants
import logger

log = logger.GetLogger(__name__, constants.LOG_FILE)

def DummyProcess(q, item):
    items = item.split()
    if len(items) == 2:
        value = items[0]
        processCount = int(items[1])
        if processCount == 0:
           log.info("handle {k}:{v} ==> {k}:{v2}".format(k=value, v=processCount, v2=processCount+1))
           q.put("{k} {v}".format(k=value, v=processCount+1))
        else:
           # handle it
           log.info("remove {k}:{v}".format(k=value,v=processCount))
        q.ack(item)

# Process item through public cloud
def DeleteRsgInternal(q, item, azLoginFunc):
    items = item.split()
    if len(items) == 2:
        value = items[0]
        processCount = int(items[1])
        azLoginFunc()
        if azureutils.IsGroupExisted(value):
           log.info("handle {k}:{v} ==> {k}:{v2}".format(k=value, v=processCount, v2=processCount+1))
           azureutils.RemoveResourceGroup(value)
           # try to delete it at most 10 times
           if processCount < 10:
              q.put("{k} {v}".format(k=value, v=processCount+1))
        else:
           # handle it
           log.info("remove {k}:{v} from queue".format(k=value,v=processCount))
        q.ack(item)

def GetQueue():
    return persistqueue.SQLiteAckQueue(constants.FileSQL)

def GetDogfoodQueue():
    return persistqueue.SQLiteAckQueue(constants.DogfoodFileSQL)

def DeleteResourceGroup():
  while True:
    q = GetQueue()
    log.info("queue size is {s}".format(s=q.size))
    if q.size != 0:
      item = q.get()
      DeleteRsgInternal(q, item, azureutils.LoginPublicCloud)
    else:
      log.info("queue is empty")
    time.sleep(constants.WaitInterval)

def PushToQueue(strVal):
   q = GetQueue()
   # put "value 0" to the queue. Mark the item unprocessed.
   q.put("{value} 0".format(value=strVal))
   log.info("an item {v} has enqueue".format(v=strVal))

def PushToDogfoodQueue(strVal):
   q = GetDogfoodQueue()
   # put "value 0" to the queue. Mark the item unprocessed.
   q.put("{value} 0".format(value=strVal))
   log.info("an item {v} has enqueue".format(v=strVal))

def DeleteDogfoodResourceGroup():
  while True:
    q = GetDogfoodQueue()
    log.info("queue size is {s}".format(s=q.size))
    if q.size != 0:
      item = q.get()
      DeleteRsgInternal(q, item, azureutils.LoginDogfood)
    else:
      log.info("queue is empty")
    time.sleep(constants.WaitInterval)
