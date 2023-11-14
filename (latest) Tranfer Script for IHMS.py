import os
import shutil
from datetime import date, timedelta
import PySimpleGUI as sg

from time import time

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Init the variables etc.

if not os.path.exists("Paths.bin"):
    sg.theme('DarkAmber')

    layout = [[sg.Text('Please run the EditTransferPaths.exe first!')]]
    PathFileError = sg.Window('Automated Data Transfer', layout)

    while True:
        event, values = PathFileError.read()
        if event in(sg.WIN_CLOSED, 'Ok'): # if user closes window or clicks close
                break

    PathFileError.close()
    exit(1)


with open("Paths.bin", "r") as f:
    PATHS = f.readlines()

SOURCE = PATHS[0].replace("\\", "/").strip()    # Read existing paths in the file
TARGET = PATHS[1].replace("\\", "/").strip()
CHKDAYS = int(PATHS[2].strip())      # Read the no. of days to check for

DATE_CHK_LIST = list()

for i in range(1, CHKDAYS+2):
    p = str(date.today() - timedelta(days = i))           # convert the dates to required format
    DATE_CHK_LIST.append(p[5:7] + p[8:] + p[:4])          # (mmddyyyy) - format in which IHMS stores files


n_copies = 0

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def compare_transfer_recursively(src, target): #(tested, working)
    """
    Recursive function to compare and transfer files from src to target(including subdirs)
    
    Uses os.listdir    : list files in given directory
         shutil.copy2  : Copy files with metadate if possible
         os.walk       : used here to get the subdirs in dir

    Then call the function to on each subdir
    """
    
    if not os.path.exists(target):  # If target folder doesnt exist, create
        os.mkdir(target)
  
    global n_copies

    src_files = os.listdir(src)
    tar_files = os.listdir(target)
    for f in src_files:      # iterate through files in SRC 
        if f not in tar_files and os.path.isfile(src + f):      # Chk if the file is not in TAR
                try:
                    shutil.copy2(src + f, target + f)
                except:
                    sg.popup(f"Unable to copy the file: {f} in {src} folder!")
                n_copies += 1

    subdirs = next(os.walk(src))[1] #gives a list of immediate subdirectories
    for sub in subdirs:
        compare_transfer_recursively(src + sub + "/", target + sub + "/")

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Window to notify transfer has begun

sg.theme('DarkAmber')
layout = [  [sg.Text('Transferring files!')],
            [sg.Text('Source Folder:       '), sg.Text(SOURCE)],
            [sg.Text('Destination Folder: '), sg.Text(TARGET)],
            [],
            
            [sg.Text('Checking upto date: '), sg.Text(DATE_CHK_LIST[-1])],
        ]

MainWindow = sg.Window('Automated Data Transfer', layout)
MainWindow.read(timeout = 1)

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Loop to call the compare_transfer_recursively() functn on all files (Main loop ig)

start = time()

for date in DATE_CHK_LIST:
    SRC_DATE = SOURCE + "/" + date + "/"
    TAR_DATE = TARGET + "/" + date + "/"
    compare_transfer_recursively(SRC_DATE, TAR_DATE)
     
end = time()

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Popup to notify transfer is complete
# Need to change this to show exceptions etc

sg.popup(f"Transfer Complete! {n_copies} files in {end - start:.3f} sec", modal = True, keep_on_top = True)
    
MainWindow.close()
