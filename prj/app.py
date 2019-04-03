#!/usr/bin/env python

# system lib
from flask import Flask, Response, request
import json
import os
import persistqueue
import threading
import time
# app lib
import azureutils
import constants
import logger
import msqueue

app = Flask(__name__)
log = logger.GetLogger(__name__, constants.LOG_FILE)

@app.route("/")
def hello():
    log.info('hello')
    return Response("Hi from your Flask app running in your Docker container!")

@app.route('/dogfood/<rsgName>', methods=['PUT'])
def createDogfoodRsg(rsgName):
    location = request.args.get('location')
    createRsgInternal(rsgName, location, True)
    return 'Create resource {rsg} on {loc} in dogfood'.format(rsg=rsgName, loc=location)

@app.route('/dogfood/<rsgName>', methods=['DELETE'])
def deleteDogfoodRsg(rsgName):
    log.info('Delete %s' % rsgName)
    msqueue.PushToDogfoodQueue(rsgName)
    return 'Delete %s' % rsgName

@app.route('/public/<rsgName>', methods=['PUT'])
def createPublicRsg(rsgName):
    location = request.args.get('location')
    createRsgInternal(rsgName, location, False)
    return 'Create resource {rsg} on {loc}'.format(rsg=rsgName, loc=location)

@app.route('/public/<rsgName>', methods=['DELETE'])
def deletePublicRsg(rsgName):
    log.info('Delete %s' % rsgName)
    msqueue.PushToQueue(rsgName)
    return 'Delete %s' % rsgName

def createRsgInternal(rsgName, location, isDogfood):
    log.info('param: {rsg} {loc}, is dogfood {d}'.format(rsg=rsgName, loc=location, d=isDogfood))
    if isDogfood:
       azureutils.LoginDogfood()
    else:
       azureutils.LoginPublicCloud()
    azureutils.CreateResourceGroup(rsgName, location)

def run():
    if os.getenv("cloud") == "dogfood":
       log.info("dogfood cloud")
       msqueue.DeleteDogfoodResourceGroup()
    else:
       log.info("public cloud")
       msqueue.DeleteResourceGroup()

def launchBgThread():
    thread = threading.Thread(target=run, args=())
    thread.daemon = True
    thread.start()

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    launchBgThread()
    app.run(os.getenv("host"), port=int(os.getenv("port")), debug=True)
