import subprocess
import json
import datetime
import time
import os
# app lib
import constants
import logger

log = logger.GetLogger(__name__, constants.LOG_FILE)

def PrintLog(msg):
   log.info(msg)

def PrintErrorLog(msg):
   log.error(msg)

def GenTimestamp():
   return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S')

def Run(cmdArgs):
   cmd = subprocess.run(cmdArgs, shell = True, stdout=subprocess.PIPE, stderr = subprocess.PIPE, check = True)
   appStdout = cmd.stdout.decode("utf-8")
   appStderr = cmd.stderr.decode("utf-8")
   rtnCode = cmd.returncode
   return (rtnCode, appStdout, appStderr)

def AzLogin(username, passwd, tenant):
   c = "az login --service-principal -u {user} --password {passwd} --tenant {tenant}".format(user=username, passwd=passwd, tenant=tenant)
   try:
     (code, out, err) = Run(c)
     PrintLog(out)
   except Exception as e:
     PrintErrorLog(e)

def UnregisterDogfood(dogfoodName):
   c = "az cloud set -n AzureCloud"
   try:
      (code, out, err) = Run(c)
   except Exception:
      PrintErrorLog("{ex}".format(ex=Exception))
   c = "az cloud list"
   try:
      (code, out, err) = Run(c)
      j = json.loads(out)
   except Exception as e:
      PrintErrorLog(e)
   exist = IsExistedName(j, dogfoodName)
   if exist:
      try:
        (code, out, err) = Run("az cloud unregister -n {x}".format(x=dogfoodName))
      except Exception as e:
        PrintErrorLog(e)

def IsExistedName(jData, targetCloud):
   exist = False
   for it in jData:
      if it['name'] == targetCloud:
          exist = True
          break
   return exist

def GetAllGroups():
   try:
     (code, out, err) = Run("az group list -o json")
     return json.loads(out)
   except Exception as e:
     PrintErrorLog(e)

def IsGroupExisted(rsg):
   jData = GetAllGroups()
   if IsExistedName(jData, rsg):
      return True
   else:
      return False

def CreateResourceGroup(rsg, location):
   jData = GetAllGroups()
   if IsExistedName(jData, rsg):
     PrintLog("Resource group '{rsg}' exists".format(rsg=rsg))
   else:
     try:
        (code, out, err) = Run("az group create --name {rsg} --location {l}".format(rsg=rsg, l=location))
        PrintLog("Successfully create {g}".format(g=rsg))
     except Exception as e:
        PrintErrorLog(e)

def RemoveResourceGroup(rsg):
   jData = GetAllGroups()
   if IsExistedName(jData, rsg):
     try:
       (code, out, err) = Run("az group delete --name {rsg} -y --no-wait".format(rsg=rsg))
       PrintLog("Successfully remove {g}".format(g=rsg))
     except Exception as e:
       PrintErrorLog(e)
   else:
     PrintLog("Resource group '{rsg}' does not exist".format(rsg=rsg))

def RegisterDogfood(dogfoodName):
   c = "az cloud list"
   exist = False
   try:
     (code, out, err) = Run(c)
     j = json.loads(out)
     exist = IsExistedName(j, dogfoodName)
   except Exception as e:
     PrintErrorLog(e)

   if exist is False:
     regDogfoodCmd = "az cloud register -n {d} --endpoint-active-directory https://login.windows-ppe.net " \
                     "--endpoint-active-directory-graph-resource-id https://graph.ppe.windows.net/ " \
                     "--endpoint-active-directory-resource-id https://management.core.windows.net/ " \
                     "--endpoint-gallery https://gallery.azure.com/ " \
                     "--endpoint-management https://umapi-preview.core.windows-int.net/ " \
                     "--endpoint-resource-manager https://api-dogfood.resources.windows-int.net/ " \
                     "--profile latest".format(d=dogfoodName)
     try:
        (code, out, err) = Run(regDogfoodCmd)
        PrintLog(out)
     except Exception as e:
        PrintErrorLog(e)
   else:
     PrintLog("{d} has already registered".format(d=dogfoodName))

def ListAllGroups():
   try:
     (code, out, err) = Run("az group list -o json")
     PrintLog(out)
     #j = json.loads(out)
     #print(j)
   except Exception as e:
     PrintErrorLog(e)

def SetCloud(cloudName):
   try:
     (code, out, err) = Run("az cloud set -n {d}".format(d=cloudName))
   except Exception as e:
     PrintErrorLog(e)

def LoginDogfood():
   un=os.getenv(constants.UserKey)
   ps=os.getenv(constants.PasswdKey)
   te=os.getenv(constants.TenantKey)
   cloud=constants.DogfoodCloud
   RegisterDogfood(cloud)
   SetCloud(cloud)
   AzLogin(un, ps, te)

def LogoutDogfood():
   un=os.getenv(constants.UserKey)
   ps=os.getenv(constants.PasswdKey)
   te=os.getenv(constants.TenantKey)
   cloud=constants.DogfoodCloud
   UnregisterDogfood(cloud)
   SetCloud(constants.PublicCloud)

def LoginPublicCloud():
   un=os.getenv(constants.UserKey)
   ps=os.getenv(constants.PasswdKey)
   te=os.getenv(constants.TenantKey)
   SetCloud(constants.PublicCloud)
   AzLogin(un, ps, te)

def TestDogfood(username, passwd, tenant):
   cloud=constants.DogfoodCloud
   RegisterDogfood(cloud)
   SetCloud(cloud)
   AzLogin(username, passwd, tenant)
   ListAllGroups()
   UnregisterDogfood(constants.DogfoodCloud)
   SetCloud(constants.PublicCloud)

def TestCreateRemoveGroupDogfood(username, passwd, tenant):
   cloud=constants.DogfoodCloud
   RegisterDogfood(cloud)
   SetCloud(cloud)
   AzLogin(username, passwd, tenant)
   g="aztest-{timestamp}".format(timestamp=GenTimestamp())
   CreateResourceGroup(g,"eastus")
   print("Created resource group")
   jData = GetAllGroups()
   if IsExistedName(jData, g):
      RemoveResourceGroup(g)
      print("Remove resource group")
   UnregisterDogfood(constants.DogfoodCloud)
   SetCloud(constants.PublicCloud)
 
def TestCreateRemoveGroup(username, passwd, tenant):
   cloud=constants.PublicCloud
   SetCloud(cloud)
   AzLogin(username, passwd, tenant)
   g="aztest-{timestamp}".format(timestamp=GenTimestamp())
   CreateResourceGroup(g,"eastus")
   print("Created resource group")
   jData = GetAllGroups()
   if IsExistedName(jData, g):
      RemoveResourceGroup(g)
      print("Remove resource group")
   SetCloud(constants.PublicCloud)

