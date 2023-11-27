import os
import shutil
import pandas as pd
import datetime

rootpath=r"C:\Users\guill\Documents\N.I.N.A"
selector= {
  "DetectedStars": 10,
  "HFR": 3,
  "GuidingRMSArcSec": 1.5
      }
  
#______________________________________________________________________________
def GuessPath(rootpath):
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
    # Load the csv file
    csvfile=os.path.join(pathinput,"ImageMetaData.csv")
    df = pd.read_csv(csvfile)
    
    # Or alternativly load the json file
    #csvfile=os.path.join(pathinput,"ImageMetaData.json")
    #df = pd.read_json(jsonfile)
    
    print(df)
    return df

#______________________________________________________________________________    
def MoveToTrash(df,trashpath):
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
def CleanUp(pathinput,df,selector):
    #Make a directory for trash
    trashpath = os.path.join(pathinput,"Trash")
    
    if not os.path.exists(trashpath):
        try:
            os.mkdir(trashpath)
        except:
            return
    print("Clean up on detected stars------------------------------------------")
    MoveToTrash(df.loc[df['DetectedStars']<selector['DetectedStars'],["FilePath"]],trashpath)
    print("Clean up on HFR----------------------------------------------------")
    MoveToTrash(df.loc[df['HFR']>selector['HFR'],["FilePath"]],trashpath)
    print("Clean up on Guiding---------------------------------------")
    MoveToTrash(df.loc[df['GuidingRMSArcSec']>selector['GuidingRMSArcSec'],["FilePath"]],trashpath)
    
#______________________________________________________________________________
#______________________________________________________________________________
# Find the Nina directory to process, either today or yesterday's date
pathinput=GuessPath(rootpath)

# Process that directory
if os.path.exists(pathinput):
    df=LoadImageMetaData(pathinput)
    CleanUp(pathinput,df,selector)
else:
    print("Nothing to process!")
    
#print(df)
