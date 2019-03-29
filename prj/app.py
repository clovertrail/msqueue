#!/usr/bin/env python

from flask import Flask, Response
import persistqueue
import time
import logger
import msqueue

app = Flask(__name__)

@app.route("/")
def hello():
    log.info('hello')
    return Response("Hi from your Flask app running in your Docker container!")

@app.route('/dogfood/<rsgName>', methods=['DELETE'])
def deleteDogfoodRsg(rsgName):
    log.info('Delete %s' % rsgName)
    msqueue.PushToQueue(rsgName, log)
    return 'Delete %s' % rsgName

if __name__ == "__main__":
    log = logger.GetLogger('clean_az_rsg', 'log.txt')
    app.run("0.0.0.0", port=80, debug=True)
    msqueue.ProcessQueue(log)
