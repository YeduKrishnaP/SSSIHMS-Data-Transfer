import PySimpleGUI as sg
import os
from datetime import datetime, timedelta
import pydicom
import logging as log
from userpaths import get_desktop
import shutil

def match_date_of_files(folder_path, date_to_match):
    files = os.listdir(folder_path)
    i = 0
    try_again = True

    while try_again and i<len(files):
        try:
                dicom_date = pydicom.dcmread(folder_path + "/" + files[i]).StudyDate
                dicom_date_in_format = datetime.strptime(dicom_date, "%Y%m%d").date().strftime("%Y-%m-%d-%a").upper()
                return dicom_date_in_format == date_to_match
        except:
            i+=1
            try_again=True

    return True

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
        log.error(f"\tSource folder doesn't exist!")
        os._exit(3)

    if not os.path.exists(target):  # If target folder doesnt exist, create
        try:
            os.mkdir(target)
        except:
            log.error("\tUnable to create target folder!\n\n")
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
                os._exit(5)

    subdirs = next(os.walk(src))[1] #gives a list of immediate subdirectories
    for sub in subdirs:
        log.debug(f"\t\t\tCalling recursion on {src + sub}\n\n")
        if match_date_of_files(src + sub, date_to_match=folder_date):
            compare_transfer_recursively(src + sub + "/", target + sub + "/", folder_date)
        else:
            log.warning(f"\t\t\tFolder containing older date studies found! Not copying {src + sub} folder!")



def convert_date_format(date_to_transfer, DATE_FORMAT):
        if DATE_FORMAT == "":
            log.error("\n\n\nNull value for DATE_FORMAT in convert_date_format!\n\n")
            os._exit(1)

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
        print(type(date_to_transfer))
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

def backup_for_specific_dates(SRC = "", DEST = "", DATES=(), DATE_FORMAT=""):
    if DATES == ():
        START_DATE = "" #expected format in dd-mm-yyyy
        END_DATE = ""
        DATE_FORMAT= ""
        help_prompt = \
    "Welcome to the Automated Data Transfer help page!\
    \n\nUsage:\n\n\
    Select the Start and the End dates for backing up the files using the calendar widgets.\n\
    After pressing Transfer Now, the app will start backing up the files to the Destination folder specified.\
    \n\nHelp with Fields:\n\n\
    1. The App can use custom date formats. Enter a string separated by spaces using the literals\n\
        described below. You can also add separators like '/' or '-' also:\n\
    (eg: yyyy - mm - dd - ddd gives date like 2024-11-23-SAT and yyyy mm dd gives 20241123)\n\n\
        yyyy: Full year (2024)\n\
        yy: Two-digit year (23)\n\
        mm: Month (01 to 12)\n\
        mmm: Abbreviated month name (e.g., 'NOV')\n\
        mmmm: Full month name (e.g., 'NOVEMBER')\n\
        dd: Day of the month (01 to 31)\n\
        ddd: Abbreviated weekday name (e.g., 'WED')\n\
        dddd: Full weekday name (e.g., 'WEDNESDAY')\n\
        w: Weekday as a number (0-6, 0=Sunday)\n\n\
        \
    Thank you for using this program! For more queries, reach out to p.yedukrishna007@gmail.com"

        layout = [
                [sg.Text('Backup Data for Specific Dates')],  
                [sg.Text('Source Folder:       '), sg.InputText(SRC, key="SRC"), sg.FolderBrowse()],
                [sg.Text('Destination Folder: '), sg.InputText(DEST, key="DEST"), sg.FolderBrowse()],
                [sg.Text('Start Date (dd-mm-yyyy):       '), sg.Input(key="START_DATE"), 
                 sg.CalendarButton(button_text="Start Date", close_when_date_chosen=True, target="START_DATE", 
                                   no_titlebar=True, format="%d-%m-%Y")],
                [sg.Text('End Date (dd-mm-yyyy):        '), sg.Input(key="END_DATE"), 
                 sg.CalendarButton(button_text="End Date", close_when_date_chosen=True, target="END_DATE", 
                                   no_titlebar=True, format="%d-%m-%Y")],
                [sg.Text('Enter the folder date format used (Kindly refer to the Help section):'), sg.InputText(DATE_FORMAT, key="DATE_FORMAT")],
                [],
                [sg.Text('Progress:')],
                [sg.ProgressBar(orientation='h', size=(650, 20), key='-PROGRESS-', max_value=1000, bar_color=("green", "brown"))],
                [sg.Button('Transfer'), sg.Button('Help'), sg.Button('Close')]
             ]
        
        sg.theme('SystemDefault')
        window = sg.Window('Automated Data Transfer', layout, grab_anywhere = True, size = (750, 300))

        while True:
            event, values = window.read()
            if event  == 'Close' or event == sg.WIN_CLOSED: 
                window.close()
                os._exit(0)
            
            elif event == 'Transfer':
                START_DATE = values["START_DATE"] 
                END_DATE = values["END_DATE"] 
                SRC = values["SRC"] 
                DEST = values["DEST"]
                DATE_FORMAT = values["DATE_FORMAT"]
                print(SRC, DEST, START_DATE, END_DATE, type(START_DATE))  

                try:
                    START_DATE = datetime.strptime(START_DATE, "%d-%m-%Y").date()
                    END_DATE = datetime.strptime(END_DATE, "%d-%m-%Y").date()
                    print("Parsed date:", START_DATE, END_DATE)

                except ValueError as e:
                    sg.popup("Invalid Date Format!", title = "Error", modal = True)
                
                if not os.path.exists(SRC):
                    sg.popup("Unable to find Source folder or doesn't exist!", title = "Error", modal = True)

                elif not os.path.exists(DEST):
                    sg.popup("Unable to find Destination folder or doesn't exist!", title = "Error", modal = True)
                    
                elif SRC == DEST:
                    sg.popup("Source and Destination are the same folder!", title = "Error")

                elif START_DATE > END_DATE:
                    sg.popup("Start date is after End dates!", title = "Error", modal = True)

                else:   #no errors
                    sg.popup("Starting transfer now. The window might get unresponsive, do not kill the program!", title = "Transferring", modal = True)

                    num_days = (END_DATE-START_DATE).days
                    if num_days ==0:
                        num_days = 1
                    window['-PROGRESS-'].update(max=num_days)

                    DATE_CHK_LIST =[]
                    current_date = START_DATE
                    log.info(f"Converting the dates to format {DATE_FORMAT}")
                    while current_date <= END_DATE:
                        DATE_CHK_LIST.append((convert_date_format(current_date, DATE_FORMAT), current_date))
                        current_date += timedelta(days=1)

                    prog = 0
                    for date_in_format, date_object in DATE_CHK_LIST:
                        print(prog, (END_DATE-START_DATE).days, date_in_format)

                        SRC_DATE = SRC + "/" + date_in_format + "/"    #assuming the source folder has all dates in the root folder
                        TAR_DATE = DEST + "/" + date_in_format + "/"
                        log.info(f"\n\n\n\n\nCalling Function on date: {SRC_DATE}")
                        compare_transfer_recursively(SRC_DATE, TAR_DATE, date_in_format)

                        prog+=1
                        window['-PROGRESS-'].update((prog+1)/num_days * 650)
                    
                    window['-PROGRESS-'].update(1000)
                    sg.popup("Transfer Complete! A log file should be created for your reference in the Desktop.", title = "Transfer Complete", modal = True)

            elif event=="Help":
                sg.popup_scrolled(help_prompt, title="Help", modal=True, size=(100, 10))
                continue   
        
if __name__ == '__main__':
    print("Start")
    log.basicConfig(filename = f"{get_desktop()}/BackupCustomDates.log", level=log.DEBUG)
    log.info("--------------------------------------------------------------------------------------------------------------------------------------------------------")
    log.info("--------------------------------------------------------------------------------------------------------------------------------------------------------")
    log.info("--------------------------------------------------------------------------------------------------------------------------------------------------------\n\n\n\n\n\n\n")
    log.info(f"Starting Program at {datetime.now()}\n\n\n")
    backup_for_specific_dates()