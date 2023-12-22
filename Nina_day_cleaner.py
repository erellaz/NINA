import os
import shutil
import pandas as pd
import datetime
from discord import SyncWebhook

# Nina data Path
rootpath=r"C:\Users\xx\Documents\N.I.N.A"

# Nina log path
NinaLogPath=r"C:\Users\xx\AppData\Local\NINA\Logs"

# Guider log path:
PHD2LogPath=r"C:\Users\xx\Documents\PHD2"

# Path to the directory used for file synchronization
syncdir=r"C:\Users\xx\Desktop\Moana-Share"

# Path to the local back up directory
backupdir=r"D:\Astro-Archive"

# Define criterium for daily produced images to pass the selection test:
selector= {
  "DetectedStars": 10,
  "HFR": 3,
  "GuidingRMSArcSec": 1.5
      }

# Web hook for the telescope Discord server
# Get Webhook from Discord>Server settings>Integration>webhooks
webhook=SyncWebhook.from_url("https://discord.com/api/webhooks/xxxxxxxxxxxX")

#______________________________________________________________________________
def newest(path):
    """Given a directory, returns the most recent file in that directory"""
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files]
    return max(paths, key=os.path.getctime)
#______________________________________________________________________________
def GuessPath(rootpath):
    """Find the NINA data directroy corresponding to either yesterday night or this morning"""
    #Nina puts the daily production in a folder year-month-day
    yesterday = datetime.datetime.now() - datetime.timedelta(1)
    ystr=datetime.datetime.strftime(yesterday, '%Y-%m-%d')

    today = datetime.datetime.now()
    tstr=datetime.datetime.strftime(today, '%Y-%m-%d')

    pathinput =os.path.join(rootpath,tstr,"LIGHT")

    if not os.path.exists(pathinput):
        pathinput =os.path.join(rootpath,ystr,"LIGHT")
    
    print(pathinput)
    return pathinput          
#______________________________________________________________________________
def LoadImageMetaData(pathinput):
    """Load the metadata file (CSV or JSON) produced by NINA the plugin called Session Meta Data"""
    # Load the csv file
    csvfile=os.path.join(pathinput,"ImageMetaData.csv")
    df = pd.read_csv(csvfile)
    
    # Or alternativly load the json file
    #jsonfile=os.path.join(pathinput,"ImageMetaData.json")
    #df = pd.read_json(jsonfile)
    
    print(df)
    return df

#______________________________________________________________________________    
def MoveToTrash(df,trashpath):
    """ Given a panda dataset with a list of files and paths move the files present in that dataset to trash"""
    #print(df)
    files=df.values.flatten()
    for file in files:
        file = file.replace('/','\\') # Seriously, NINA?
        print("move ",file,trashpath)
        try:
            shutil.move(file,trashpath) 
        except:
            pass
    
#______________________________________________________________________________
def CleanUp(pathinput,df,selector,webhook):
    """ Given a panda dataset from NINA SESSION METADATA, move the files present in that dataset to trash depending on SELECTOR condition"""
    #Make a directory for trash
    trashpath = os.path.join(pathinput,"Trash")
    
    if not os.path.exists(trashpath):
        try:
            os.mkdir(trashpath)
        except:
            return
    
    webhook.send("Total number of files: "+str(df['DetectedStars'].count()))
    print("Total number of files: "+str(df['DetectedStars'].count()))
    
    print("Clean up on detected stars------------------------------------------")
    webhook.send("Removing files due to not enough stars: "+str(df.loc[df['DetectedStars']<selector['DetectedStars']].shape[0]))
    print("Removing files due to not enough stars: "+str(df.loc[df['DetectedStars']<selector['DetectedStars']].shape[0]))
    MoveToTrash(df.loc[df['DetectedStars']<selector['DetectedStars'],["FilePath"]],trashpath)
    
    print("Clean up on HFR----------------------------------------------------")
    webhook.send("Removing files due to bad HFR: "+str(df.loc[df['HFR']>selector['HFR']].shape[0]))
    print("Removing files due to bad HFR: "+str(df.loc[df['HFR']>selector['HFR']].shape[0]))
    MoveToTrash(df.loc[df['HFR']>selector['HFR'],["FilePath"]],trashpath)
    
    print("Clean up on Guiding---------------------------------------")
    webhook.send("Removing files due to bad guiding: "+str(df.loc[df['GuidingRMSArcSec']>selector['GuidingRMSArcSec']].shape[0]))
    print("Removing files due to bad guiding: "+str(df.loc[df['GuidingRMSArcSec']>selector['GuidingRMSArcSec']].shape[0]))
    MoveToTrash(df.loc[df['GuidingRMSArcSec']>selector['GuidingRMSArcSec'],["FilePath"]],trashpath)
    
#______________________________________________________________________________
#______________________________________________________________________________
# Find the Nina directory to process, either today or yesterday's date
pathinput=GuessPath(rootpath)

# Process that directory
if os.path.exists(pathinput):
    webhook.send("Python deamon is initiating production cleanup from NINA logs.")
    df=LoadImageMetaData(pathinput)
    #print(df)
    CleanUp(pathinput,df,selector,webhook)
    webhook.send("Python deamon is done cleaning daily production.")
    webhook.send("Backing up PHD2 log, Nina log and NINA Sequence file.")
    
    NinaLogNewest=newest(NinaLogPath)
    try:
        shutil.copy(NinaLogNewest,pathinput) 
    except:
        print("Failed to copy Nina Log")
    
    PHD2LogNewest=newest(PHD2LogPath)
    try:
        shutil.copy(PHD2LogNewest,pathinput) 
    except:
        print("Failed to copy PHD2 log")
        
    webhook.send("Saving all NINA JSON files")   
    try:
        for basename in os.listdir(rootpath):
            if basename.endswith('.json'):
                pathname = os.path.join(rootpath, basename)
                if os.path.isfile(pathname):
                    shutil.copy2(pathname, pathinput)
    except:
        print("Failed to back up NINA JSON files")   

    webhook.send("Create a local back up of daily production")
    try:
        # Trick: to get a folder up just use os.path.dirname twice back to back
        shutil.copytree(os.path.dirname(pathinput),os.path.join(backupdir,os.path.basename(os.path.dirname(pathinput)))) 
        webhook.send("Copied: "+os.path.dirname(pathinput)+" to "+backupdir)
    except:
        print("Failed to copy",os.path.dirname(pathinput)," to ",backupdir," production to backup directory")
        webhook.send("Failed to copy production to backup directory: "+os.path.dirname(pathinput)+" to "+backupdir)     
    
    webhook.send("Moving daily production to Sync folder")
    try:
        # Trick: to get a folder up just use os.path.dirname twice back to back
        shutil.move(os.path.dirname(pathinput),syncdir) 
        webhook.send("Moved: "+os.path.dirname(pathinput)+" to "+syncdir)
    except:
        print("Failed to Move production to Sync directory")
        webhook.send("Failed to Move production to Sync directory") 
    
else:
    print("Nothing to process!")
    webhook.send("Python deamon found nothing to clean up.")

#________________________________________________________________________________   
# In any case check the pdus and shut down if needed

import dlipower
#if you get this error: 
# Digital Loggers Web Powerswitch 192.168.xx.xx:xxx (UNCONNECTED)
# Go to the PDU admin page and change:
# Allow legacy plaintext login methods (enable)
# Then also allow this if the outlet cannot be changed by the script:
# Allow legacy state-changing GET requests

hostname=r"192.168.xx.xx:xxx" 
userid="xx"
password="xx"

print('Connecting to DLI PowerSwitch:',hostname, userid, password)

switch = dlipower.PowerSwitch(hostname=hostname, userid=userid, password=password,use_https=False)

print(switch)

# Checking and switching off only the PDUs in the group before
# in particular pdu 0, the computer needs to stay on
for i in [1, 2, 3, 4]:
    if switch[i].state != "OFF":
        webhook.send("ALERT: PDU ",i," seems to be still ON, switching OFF")
        status1=switch.off(outlet=i)
        
    
webhook.send("Checking the status of the PDUs"+str(switch))
print(switch)

webhook.send("Python deamon: all done, see ya tomorrow!") 
