# -*- coding: utf-8 -*-

import os
import shutil
from datetime import date, timedelta
import PySimpleGUI as sg

from time import time


#-----------------------------------------------------------------------------
#Init the variables etc.

"""if not os.path.exists("Paths.bin"):
     # code to handle """

with open("Paths.bin", "r") as f:
    PATHS = f.readlines()

SOURCE = PATHS[0].replace("\\", "/").strip()    # Read existing paths in the file
TARGET = PATHS[1].replace("\\", "/").strip() 

t = str(date.today() - timedelta(days = 1))     # convert the dates to required format
TARGET_DATE = t[5:7] + t[8:] + t[:4]            # (mmddyyyy) - format in which IHMS stores files
#print(f"Target date in format: {TARGET_DATE}\t\t{t}")

p = str(date.today() - timedelta(days = 2))
PREV_DATE = p[5:7] + p[8:] + p[:4]
#print(f"Previous date in format: {PREV_DATE}\t{p}")

present_dir = SOURCE + "/" + TARGET_DATE + "/"
prev_src = SOURCE + "/" + PREV_DATE + "/"
prev_tar = TARGET + "/" + PREV_DATE + "/"
tar_dir = TARGET + "/" + TARGET_DATE + "/"

n_copies = 0

print(present_dir, tar_dir, prev_src, prev_tar, sep = "\n\n")

#-----------------------------------------------------------------------------

def compare_transfer_recursively(src, target): #(tested, working)
    """
    Recursive function to compare and transfer files from src to target(including subdirs)
    
    Uses os.listdir    : list files in given directory
         shutil.copy2  : Copy files with metadate if possible
         os.walk       : used here to get the subdirs in dir

    Then call the function to on each subdir

    """
    
    print("-----------------------------------------------------------------------------")
    print(f"Source: {src}\ntarget: {target}")
    if not os.path.exists(target):  # If target folder doesnt exist, create
        print(f"Creating folder: {target}")
        os.mkdir(target)

    global n_copies
    print("\n\n")

    src_files = os.listdir(src)
    tar_files = os.listdir(target)
    for f in src_files: # iterate through files in SRC 
        if f not in tar_files and os.path.isfile(src + f): # Chk if the file is not in TAR
                #print(f"Copying pending: \n{src + f} \n | \n{target + f}\n\n")
                shutil.copy2(src + f, target + f)
                n_copies += 1

    subdirs = next(os.walk(src))[1] #gives a list of immediate subdirectories
    print(f"Subdirectories found: {subdirs}")
    print(f"\n\nNo. of completed transfers from current directory: {n_copies}\n\n")
    for sub in subdirs:
        compare_transfer_recursively(src + sub + "/", target + sub + "/")

#-----------------------------------------------------------------------------
# Call the function for yesterday and day-before's files

start = time()
compare_transfer_recursively(prev_src, prev_tar)

compare_transfer_recursively(present_dir, tar_dir)
end = time()


#------------------------------------------------------------------------------
# The Interface to notify transfer is complete
# Need to change this to show exceptions etc


sg.theme('DarkAmber')


layout = [  [sg.Text('Successfully completed the transfer for today')],
            [sg.Text('Source Folder:       '), sg.Text(SOURCE)],
            [sg.Text('Destination Folder: '), sg.Text(TARGET)],
            [],
            [sg.Text(f'No. of transfers completed: {n_copies} in {end - start:.3f} sec')],
            [sg.Text('{Add option for checking upto given date etc}')],
            [sg.Button('Ok')]
        ]

window = sg.Window('Automated Data Transfer', layout)

while True:
    event, values = window.read()
    if event in(sg.WIN_CLOSED, 'Ok'): # if user closes window or clicks close
        break
    
window.close()
