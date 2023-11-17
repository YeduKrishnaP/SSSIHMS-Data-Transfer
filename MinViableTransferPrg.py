import os
import shutil
from datetime import date, timedelta
import logging as log

#-----------------------------------------------------------------------------
#Init the variables etc.

log.basicConfig(filename = f"./Logfiles/{date.today()}.log", level=log.DEBUG)
log.info("--------------------------------------------------------------------------------------------------------------------------------------------------------")
log.info("--------------------------------------------------------------------------------------------------------------------------------------------------------")
log.info("--------------------------------------------------------------------------------------------------------------------------------------------------------\n\n\n\n\n\n\n")
log.info("Starting Program")

try:
    with open("Paths.bin", "r") as f:
        PATHS = f.readlines()
except:
    log.error("Unable to open Paths.bin")
    exit(1)

try:
    SOURCE = PATHS[0].replace("\\", "/").strip()    # Read existing paths in the file
    TARGET = PATHS[1].replace("\\", "/").strip()
    CHKDAYS = int(PATHS[2].strip())                 # Read the no. of days to check for
    
except:
    log.error("Error in reading the data from Paths.bin")
    exit(2)
    
DATE_CHK_LIST = list()
for i in range(1, CHKDAYS+1):
    p = str(date.today() - timedelta(days = i)) # convert the dates to required format
    DATE_CHK_LIST.append(p[5:7] + p[8:] + p[:4])# (mmddyyyy) - format in which IHMS stores files

log.info(f"Dates to check: {DATE_CHK_LIST}")
    
#-----------------------------------------------------------------------------

def compare_transfer_recursively(src, target): #(tested, working)
    """
    Recursive function to compare and transfer files from src to target(including subdirs)
    
    Uses os.listdir    : list files in given directory
         shutil.copy2  : Copy files with metadate if possible
         os.walk       : used here to get the subdirs in dir

    Then call the function to on each subdir
    """

    log.debug(f"\tCurrent SRC: {src} | Tar: {target}")
    
    if not os.path.exists(target):  # If target folder doesnt exist, create
        os.mkdir(target)

    src_files = os.listdir(src)
    tar_files = os.listdir(target)

    
    for f in src_files: # iterate through files in SRC 
        if f not in tar_files and os.path.isfile(src + f): # Chk if the file is not in TAR
            try:
                shutil.copy2(src + f, target + f)
                log.debug(f"\t\t\tCopying {src + f} to {target + f}")
            except:
                log.error("Failed to copy file: {f}\n")

    subdirs = next(os.walk(src))[1] #gives a list of immediate subdirectories
    for sub in subdirs:
        log.debug(f"\t\t\t\n\nCalling recursion on {src + sub}\n\n")
        compare_transfer_recursively(src + sub + "/", target + sub + "/")
        
#-----------------------------------------------------------------------------
# Call the function for folders in DATE_CHK_LIST

for date in DATE_CHK_LIST:
    SRC_DATE = SOURCE + "/" + date + "/"
    TAR_DATE = TARGET + "/" + date + "/"
    log.debug(f"\n\n\n\n\nCalling Function on date: {SRC_DATE}")
    compare_transfer_recursively(SRC_DATE, TAR_DATE)

log.info("\n\n\n\n\nCompleted Transfer Successfully!\n\n\n\n\n\n\n\n")
