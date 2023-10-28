# -*- coding: utf-8 -*-

import os
import shutil
from filecmp import dircmp, cmpfiles
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
TARGET = PATHS[1].replace("\\", "/").strip()    # if it exists

t = str(date.today() - timedelta(days = 1))     # convert the dates to required format
TARGET_DATE = t[5:7] + t[8:] + t[:4]            # (mmddyyyy)
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
    Recursive to compare and transfer files from src to target(including subdirs)

    Implemented using filecmp module function: dircmp
    Documentation: https://docs.python.org/3/library/filecmp.html
    
    dircmp returns directory comparison object
    

    """
    print("-----------------------------------------------------------------------------")
    print(f"Source: {src}\ntarget: {target}")
    if not os.path.exists(target):  # If target folder doesnt exist, create
        print(f"Creating folder: {target}")
        os.mkdir(target)

    global n_copies
    print("\n\n")

    comp_obj = dircmp(src, target) 
    for f in comp_obj.left_only: # iterate through files in SRC 
        if f not in comp_obj.right_only and os.path.isfile(src + f): # Chk if the file is not in TAR
                print(f"Copying pending: \n{src + f} \n | \n{target + f}\n\n") # Copy
                shutil.copy2(src + f, target + f)
                n_copies += 1

    subdirs = next(os.walk(src))[1] #gives a list of immediate subdirectories
    print(f"Subdirectories found: {subdirs}")
    print(f"\n\nNo. of completed transfers from current directory: {n_copies}\n\n")
    for sub in subdirs:
        compare_transfer_recursively(src + sub + "/", target + sub + "/")

#-----------------------------------------------------------------------------


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
