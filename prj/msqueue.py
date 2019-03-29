#!/usr/bin/env python

import persistqueue
import time
import logger

FileSQL="sqlite.ack.queue"

def DummyProcess(q, item, log):
    items = item.split()
    if len(items) == 2:
        value = items[0]
        processCount = int(items[1])
        if processCount == 0:
           log.info("handle {k}:{v} ==> {k}:{v2}".format(k=value, v=processCount, v2=processCount+1))
           q.ack(item)
           q.put("{k} {v}".format(k=value, v=processCount+1))
        else:
           # handle it
           log.info("remove {k}:{v}".format(k=value,v=processCount))
           q.ack(item)

def ProcessQueue(log):
  while True:
    q = persistqueue.SQLiteAckQueue(FileSQL)
    log.info("queue size is {s}".format(s=q.size))
    if q.size != 0:
      item = q.get()
      items = item.split()
      DummyProcess(q, items, log)
    else:
      log.info("queue is empty")
    time.sleep(1)

def PushToQueue(strVal, log):
   q = persistqueue.SQLiteAckQueue(FileSQL)
   # put "value 0" to the queue. Mark the item unprocessed.
   q.put("{value} 0".format(value=strVal))
   log.info("an item {v} has enqueue".format(v=strVal))
