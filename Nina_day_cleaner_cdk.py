import os
import shutil
import pandas as pd
import datetime
import zipfile
from discord import SyncWebhook

# Nina data Path
rootpath=r"C:\Users\xx\Documents\N.I.N.A"

# Nina log path
NinaLogPath=r"C:\Users\xx\AppData\Local\NINA\Logs"

# Guider log path:
PHD2LogPath=r"C:\Users\xx\Documents\PHD2"

# Path to the directory used for file synchronization
syncdir=r"C:\Users\xx\Desktop\Share"

# Path to the local back up directory
#backupdir=r"D:\Astro-Archive"
backupdir=r"D:\Astro-Archive"

# Define criterium for daily produced images to pass the selection test:
selector= {
  "DetectedStars": 50,
  "HFR": 4.5,
  "GuidingRMSArcSec": 1.5
      }

# Web hook for the telescope Discord server
# Get Webhook from Discord>Server settings>Integration>webhooks
webhook=SyncWebhook.from_url(r"https://discord.com/api/webhooks/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

# Verbosity: 0=quiet, 1 st dout, 2 std out and discord
verbosity=2


#______________________________________________________________________________
def Talk(verbosity, message, webhook=None):
    if verbosity >= 1:
        print(message)
    if verbosity >= 2 and webhook is not None:  
       try:
           webhook.send(message)
       except Exception as e:
           print("Exception while posting to Discord",e,message)
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

    #pathinput =os.path.join(rootpath,tstr,"LIGHT")
    pathinput =os.path.join(rootpath,tstr)
    
    if not os.path.exists(pathinput):
        #pathinput =os.path.join(rootpath,ystr,"LIGHT")
        pathinput =os.path.join(rootpath,ystr)
        
    print(pathinput)
    return pathinput,ystr         
#______________________________________________________________________________
def LoadImageMetaData(pathinput):
    """Load the metadata file (CSV or JSON) produced by NINA the plugin called Session Meta Data"""
    # Load the csv file
    #csvfile=os.path.join(pathinput,"ImageMetaData.csv") # Before NINA 3
    csvfile=os.path.join(rootpath,"ImageMetaData.csv") # For Nina 3 and up
    df = pd.read_csv(csvfile)
    
    # Or alternativly load the json file
    #jsonfile=os.path.join(pathinput,"ImageMetaData.json") # Before NINA 3
    #jsonfile=os.path.join(rootpath,"ImageMetaData.json") # For Nina 3 and up
    #df = pd.read_json(jsonfile)
    
    print(df)
    return df

#______________________________________________________________________________
def FilterDataset(df,ystr,column_name='FilePath'):
    # filter the dataset based on values in column, for example if the FilePath column contains a certain date
    df_filtered = df[df[column_name].str.contains(ystr)]
    return df_filtered 

#______________________________________________________________________________    
def MoveToTrash(df,trashpath):
    """ Given a panda dataset with a list of files and paths move the files present in that dataset to trash"""
    #print(df)
    files=df.values.flatten()
    for file in files:
        file = file.replace('/','\\')+".zip"# Seriously, NINA?
        Talk(1,"move "+ file + " to "+ trashpath)
        try:
            shutil.move(file,trashpath) 
        except:
            Talk(1,file + " Exception - skipping! ")
            pass
    
#______________________________________________________________________________
def CleanUp(pathinput,df,selector,verbosity,webhook):
    """ Given a panda dataset from NINA SESSION METADATA, move the files present in that dataset to trash depending on SELECTOR condition"""
    #Make a directory for trash
    trashpath = os.path.join(pathinput,"Trash")
    
    if not os.path.exists(trashpath):
        try:
            os.mkdir(trashpath)
        except:
            return
    
    Talk(verbosity,"Total number of files: "+str(df['DetectedStars'].count()),webhook)
    
    Talk(verbosity,"Removing files due to not enough stars: "+str(df.loc[df['DetectedStars']<selector['DetectedStars']].shape[0]),webhook)
    MoveToTrash(df.loc[df['DetectedStars']<selector['DetectedStars'],["FilePath"]],trashpath)
    
    Talk(verbosity,"Removing files due to bad HFR: "+str(df.loc[df['HFR']>selector['HFR']].shape[0]),webhook)
    MoveToTrash(df.loc[df['HFR']>selector['HFR'],["FilePath"]],trashpath)
    
    Talk(verbosity,"Removing files due to bad guiding: "+str(df.loc[df['GuidingRMSArcSec']>selector['GuidingRMSArcSec']].shape[0]),webhook)
    MoveToTrash(df.loc[df['GuidingRMSArcSec']>selector['GuidingRMSArcSec'],["FilePath"]],trashpath)

#______________________________________________________________________________
def FitsCompressor(source_dir,dest_dir,verbosity,webhook):
    """ Compress all the fits files in a directory"""

    target_pattern='.fits'

    Talk(verbosity,"Compressing fits files",webhook)

    def target_files(source_dir):
        for filename in os.listdir(source_dir):
            if filename.endswith(target_pattern):
                yield filename

    os.chdir(source_dir)  # To work around zipfile limitations

    for target_filename in target_files(source_dir):
        file_root = os.path.splitext(target_filename)[0]
        zip_file_name = file_root + target_pattern+ '.zip'
        zip_file_path = os.path.join(dest_dir, zip_file_name)
        Talk(1,"Compressing "+target_filename,None)
        #DEFLATED or LZMA compression
        with zipfile.ZipFile(zip_file_path, mode='w',compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            zf.write(target_filename)
            zf.close() #file should be closed automatically in a with statement
        os.remove(target_filename)  
    os.chdir(dest_dir)

#______________________________________________________________________________
#______________________________________________________________________________
# Find the Nina directory to process, either today or yesterday's date
pathinput,ystr=GuessPath(rootpath)


# Process that directory
if os.path.exists(pathinput):
    Talk(verbosity,"Python deamon is initiating production cleanup from NINA logs.",webhook)
    
    dfall=LoadImageMetaData(pathinput) # load all the metadata
    df=FilterDataset(dfall,r"N.I.N.A/"+ystr) # keep only the relevant date in the dataset
    #print(df)
    FitsCompressor(pathinput,pathinput,verbosity,webhook)
    CleanUp(pathinput,df,selector,verbosity,webhook)
    Talk(verbosity,"Python deamon is done cleaning daily production.",webhook)
    Talk(verbosity,"Backing up PHD2 log, Nina log and NINA Sequence file.",webhook)
    
    Metapath = os.path.join(pathinput,"Meta"+ystr)
    if not os.path.exists(Metapath):
        try:
            os.mkdir(Metapath)
        except:
            Talk(verbosity,"Failed to Create Meta directory",webhook)
        
    NinaLogNewest=newest(NinaLogPath)
    try:
        shutil.copy(NinaLogNewest,Metapath) 
    except:
        Talk(verbosity,"Failed to copy Nina Log",webhook)
    
    PHD2LogNewest=newest(PHD2LogPath)
    try:
        shutil.copy(PHD2LogNewest,Metapath) 
    except:
        Talk(verbosity,"Failed to copy PHD2 log",webhook)
        
    Talk(verbosity,"Saving all NINA JSON files",webhook)   
    try:
        for basename in os.listdir(rootpath):
            if basename.endswith('.json'):
                pathname = os.path.join(rootpath, basename)
                if os.path.isfile(pathname):
                    shutil.copy2(pathname, Metapath)
    except:
        Talk(verbosity,"Failed to back up NINA JSON files",webhook)   

    Talk(verbosity,"Create a local back up of daily production",webhook)
    
    os.chdir(pathinput)
    try:
        # Trick: to get a folder up just use os.path.dirname twice back to back
        outputdir=os.path.join(syncdir,ystr)
        shutil.copytree(pathinput,outputdir) 
        Talk(verbosity,"Copied: " + pathinput + " to " + outputdir,webhook)
    except Exception as e:
        Talk(verbosity,"Failed to copy production to backup directory: "+ pathinput + " to " + outputdir + e,webhook)
    
    try:
        # Trick: to get a folder up just use os.path.dirname twice back to back
        outputdir=os.path.join(backupdir,ystr)
        shutil.copytree(pathinput,outputdir) 
        Talk(verbosity,"Copied: " + pathinput+" to " + outputdir,webhook)
    except Exception as e:
        Talk(verbosity,"Failed to copy production to backup directory: "+ pathinput+" to " + outputdir + e,webhook)     
    

    
else:
    Talk(verbosity,"Nothing to process!",webhook)
    Talk(verbosity,"Python deamon found nothing to clean up.",webhook)

#________________________________________________________________________________   
