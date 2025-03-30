import os
import shutil
from datetime import date, timedelta, datetime
import logging as log
from EmailClient import SendLogs
from userpaths import get_local_appdata
from Encryption import decrypt_data
import pydicom
from GdriveHelper import launch_gdrive

"""
SendLogs send a mail to the user depending on the following codes:
    0 - successful completion
    1 - Unable to find Paths.bin
    2 - 
    3 - Source Folder missing
    4 - Unable to create target folder
    5 - shutil.copy2 failed on file
"""

def convert_date_format(date_to_transfer, DATE_FORMAT):
        format_map = {
            'yyyy': '%Y',   # Full year (2024)
            'yy': '%y',     # Two-digit year (24)
            'mm': '%m',     # Month (01 to 12)
            'mmm': '%b',    # Abbreviated month name (e.g., 'Nov')
            'mmmm': '%B',   # Full month name (e.g., 'November')
            'dd': '%d',     # Day of the month (01 to 31)
            'ddd': '%a',    # Abbreviated weekday name (e.g., 'Wed')
            'dddd': '%A',   # Full weekday name (e.g., 'Wednesday')
            'w': '%w',      # Weekday as a number (0-6, 0=Sunday)
        }

        parts = DATE_FORMAT.split(' ')

        formatted_parts = []
        for part in parts:
            if part in format_map:
                if part in ['mmm', 'mmmm', 'ddd', 'dddd']:
                    formatted_parts.append(date_to_transfer.strftime(format_map[part]).upper())
                else:
                    formatted_parts.append(date_to_transfer.strftime(format_map[part]))
            else:
                formatted_parts.append(part)
        return ''.join(formatted_parts)

def match_date_of_files(folder_path, date_to_match):
    files = os.listdir(folder_path)
    i = 0
    try_again = True

    while try_again and i<len(files):
        try:
                dicom_date = pydicom.dcmread(folder_path + "/" + files[0]).StudyDate
                dicom_date_in_format = datetime.strptime(dicom_date, "%Y%m%d").date().strftime("%Y-%m-%d-%a").upper()
                return dicom_date_in_format == date_to_match
        except:
            try_again=True

    return True # incase none of the files are in dicom format or unable to read them, copy the subfolder


def compare_transfer_recursively(src, target, folder_date): #(tested, working)
    """
    Recursive function to compare and transfer files from src to target(including subdirs)
    
    Uses os.listdir    : list files in given directory
         shutil.copy2  : Copy files with metadate if possible
         os.walk       : used here to get the subdirs in dir

    Then call the function to on each subdir
    """

    log.debug(f"\tCurrent SRC: {src} | Tar: {target}")

    if not os.path.exists(src):
        log.error(f"\tSource folder doesn't exist! {src}")
        SendLogs(3)
        os._exit(3)

    if not os.path.exists(target):  # If target folder doesnt exist, create
        try:
            os.mkdir(target)
        except:
            log.error(f"\tUnable to create target folder! {target}\n\n")
            SendLogs(4)
            os._exit(4)

    src_files = os.listdir(src)
    tar_files = os.listdir(target)

    for f in src_files: # iterate through files in SRC 
        if f not in tar_files and os.path.isfile(src + f): # Chk if the file is not in TAR
            try:
                try:
                    dicom_date = pydicom.dcmread(src + f).StudyDate
                    dicom_date_in_format = datetime.strptime(dicom_date, "%Y%m%d").date().strftime("%Y-%m-%d-%a").upper()
                    if folder_date == dicom_date_in_format:
                        log.debug(f"\t\t\tCopying {src + f} to {target + f}")
                        shutil.copy2(src + f, target + f)

                    else:
                        log.warning(f"\t\t\tDICOM file {f} with older study date found! Not copying the file!")

                except:
                    log.warning("Unable to parse file in DICOM format! Copying it anyways!")
                    log.debug(f"\t\t\tCopying {src + f} to {target + f}")
                    shutil.copy2(src + f, target + f)

            except:
                log.error(f"Failed to copy file: {f}\n")
                SendLogs(5)
                os._exit(5)

    subdirs = next(os.walk(src))[1] #gives a list of immediate subdirectories
    for sub in subdirs:
        log.debug(f"\t\t\tCalling recursion on {src + sub}\n\n")
        # if match_date_of_files(src + sub, date_to_match=folder_date):
        compare_transfer_recursively(src + sub + "/", target + sub + "/", folder_date)
        # else:
        #     log.warning(f"\t\t\tFolder containing older date studies found! Not copying {src + sub} folder!")

#-----------------------------------------------------------------------------

def main():
#Init the variables etc.
    docs_path = get_local_appdata() + "/AutomatedDataTransfer"
    PATHS_FILE = get_local_appdata() + "\\AutomatedDataTransfer\\Paths.adt"

    if not os.path.exists(docs_path + "/Logfiles"):
        os.mkdir(docs_path + "/Logfiles")

    log.basicConfig(filename = f"{docs_path}/Logfiles/{date.today()}.log", level=log.DEBUG)
    log.info("--------------------------------------------------------------------------------------------------------------------------------------------------------")
    log.info("--------------------------------------------------------------------------------------------------------------------------------------------------------")
    log.info("--------------------------------------------------------------------------------------------------------------------------------------------------------\n\n\n\n\n\n\n")
    log.info(f"Starting Program at {datetime.now()}\n\n\n")

    try:
            log.info("Opened the Paths.adt sucessfully! Reading data")
            PATHS = decrypt_data(PATHS_FILE)

            SOURCE = PATHS[0].replace("\\", "/").strip()    # Read existing paths in the file
            TARGET = PATHS[1].replace("\\", "/").strip()
            CHKDAYS = int(PATHS[2].strip())                 # Read the no. of days to check for
            DATE_FORMAT = PATHS[3]

    except:
        log.error("Unable to read Paths.adt")
        SendLogs(1)
        os._exit(1)
        
    DATE_CHK_LIST = list()
    YEAR = str(date.today())[:4]
    for i in range(CHKDAYS+1):
        date_to_transfer = date.today() - timedelta(days = i) # convert the dates to required format
        DATE_CHK_LIST.append((convert_date_format(date_to_transfer, DATE_FORMAT), date_to_transfer))    # look for dates in specified format 

    log.info(f"Dates to check: {DATE_CHK_LIST}")

    #-----------------------------------------------------------------------------
    # Call the function for folders in DATE_CHK_LIST

    for date_in_format, date_object in DATE_CHK_LIST:
        SRC_DATE = SOURCE + "/" + date_in_format + "/"    #assuming the source folder has all dates in the root folder
    
        # The following has been removed due to maintain folder structures across target and source

        # TAR_MONTH = TARGET + "/" + calendar.month_name[date_object.month] + " " + YEAR + "/" #puts the files in MARCH2024 etc. at target
        # if not os.path.exists(TAR_MONTH):
        #     os.mkdir(TAR_MONTH)
        
        TAR_DATE = TARGET + "/" + date_in_format + "/"
        log.info(f"\n\n\n\n\nCalling Function on date: {SRC_DATE}")
        compare_transfer_recursively(SRC_DATE, TAR_DATE, date_in_format)

    log.info("\n\n\n\n\nCompleted Transfer Successfully!\n\n\n\n\n\n\n\n")
    # SendLogs(0)
    os._exit(0)

if __name__ == "__main__":
    docs_path = get_local_appdata() + "/AutomatedDataTransfer"
    PATHS_FILE = get_local_appdata() + "\\AutomatedDataTransfer\\Paths.adt"

    if not os.path.exists(docs_path + "/Logfiles"):
        os.mkdir(docs_path + "/Logfiles")

    log.basicConfig(filename = f"{docs_path}/Logfiles/{date.today()}.log", level=log.DEBUG)
    log.info("--------------------------------------------------------------------------------------------------------------------------------------------------------")
    log.info("--------------------------------------------------------------------------------------------------------------------------------------------------------")
    log.info("--------------------------------------------------------------------------------------------------------------------------------------------------------\n\n\n\n\n\n\n")
    log.info(f"Starting Program at {datetime.now()}\n\n\n")
    launch_gdrive()
    main()