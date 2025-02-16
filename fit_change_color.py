# -*- coding: utf-8 -*-
import os
from astropy.io import fits


pathinput =r"D:\Pixinsight\CDK14\Data\NGC4038\tmp"

#____________________________________________________________________________________________________
# Change the lat long in fit file, or change any other header
def change_fit_header(fits_file):
    print("Sanitizing: ",fits_file)
    with fits.open(fits_file, mode='update') as hdul:
        hdr = hdul[0].header
        hdr['FILTER']=('Lum', 'Active Filter name')
        hdul.flush()  # changes are written back to original.fits
#____________________________________________________________________________________________________  
# Iterate for every fit in the directory
def change_all_headers(pathinput):
    dirsinput = os.listdir( pathinput )
    for item in dirsinput:
        split_item = os.path.splitext(item)
        print(item,split_item[1],os.path.isfile(pathinput+item))
        if (split_item[1]==".fit" or split_item[1]==".fits"):
            print("Changing header",pathinput,item) ##### Wrong------------------------
            change_fit_header(os.path.join(pathinput,item))
            


#____________________________________________________________________________________________________            
change_all_headers(pathinput)
