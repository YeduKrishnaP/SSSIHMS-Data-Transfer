import PySimpleGUI as sg
import os
from subprocess import run
import win32com.client
from datetime import datetime, timedelta, date
from pyuac import isUserAdmin, runAsAdmin
from userpaths import get_local_appdata
from Encryption import encrypt, decrypt_data
from shutil import copy2

def Create_Task(user_password, TIME):   #Creates a Task Scheduler Task for the TransferPrg.exe
    """
    Write the doc here
    """
    cur_user = os.getlogin()
    computer_name = os.environ['COMPUTERNAME']
    
    TOMORROW_DATE = (datetime.now() + timedelta(1)).strftime('%Y-%m-%d')
    START = TOMORROW_DATE + "T" + TIME.strftime('%H:%M:%S')
    
    cur_dir = os.getcwd()
    exe_file = cur_dir + "\\" + "TransferPrg.exe"

    if not os.path.exists(exe_file):
        return "MISSING_EXE"

    SCH = win32com.client.Dispatch('Schedule.Service')
    SCH.Connect()
    root = SCH.GetFolder('\\')
    TASK = SCH.NewTask(0)

    TriggerType = 2 #Daily
    trigger = TASK.Triggers.Create(TriggerType)
    trigger.StartBoundary = START
    trigger.DaysInterval = 1
    trigger.Enabled = True
    trigger.Id = "DailyTrigger"
    action = TASK.Actions.Create(0) # 0 refers to the type execute
    action.Path = exe_file
    action.ID = "AutomatedDataTransfer"
    action.WorkingDirectory = cur_dir
    TASK.RegistrationInfo.Description = "Testing ADT scheduling using pywin32"
    TASK.Settings.Enabled = True
    TASK.Settings.StopIfGoingOnBatteries = False
    TASK.Settings.RunOnlyIfIdle = False
    TASK.Settings.StartWhenAvailable = True
    TASK.Settings.DisallowStartIfOnBatteries = False

    task_create_or_update = 6
    task_logon_none = 1
    TASK.Principal.UserId = cur_user
    TASK.Principal.LogonType = 6

    try:  
        root.RegisterTaskDefinition(
            "AutomatedDataTransfer",
            TASK,
            task_create_or_update,
            f"{cur_user}",
            user_password,
            task_logon_none
            )
        
        return "SUCCESS"
    
    except:
        return "FAILED"
    
def check_date_format(DATE_FORMAT):
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
        for part in parts:
            if part not in format_map:
                return "INVALID DATE FORMAT"
        
        return DATE_FORMAT
    

def INIT_PATHS_FILE():
    """
    Function that creates a file to store the paths of the Source and Destination
    folders for the Automated Backup Program to read

    Libraries used: PySimpleGUI, OS
    """    

    sg.theme('SystemDefault')
    CUR_DIR = os.getcwd()
    PATHS_FILE = get_local_appdata() + "\\AutomatedDataTransfer\\Paths.adt" # encrypted adt file
    SRC = ""
    DEST = ""
    CHKDATES = "(eg: 3 means the program checks 3 previous days for consistency)"
    DATE_FORMAT = 'yyyy - mm - dd - dddd'
    time_prompt = "Enter in 24Hr format hh:mm:ss (eg: 18:00:00)"
    help_prompt = \
    "Welcome to the Automated Data Transfer help page!\
    \n\nUsage:\n\n\
    First fill the fields in the current window and proceed to click on Ok to open the 'Mail Client'\n\
    You can either fill it for mail notifications or ignore. Then click on 'Return'.\n\
    Then if necessary, click on 'Transfer Now' to test the transfer proram.\n\nHelp with Fields:\n\n\
    1. No. Of days to check for consistency refers to the number of days you want the program\n\
    to check for consistency between the Source and the Destination.\n\n\
    For example: if the Source has the folders\n\n\
    12012023    (01-12-2023)\n\
    12022023    (02-12-2023)\n\
    12032023    (03-12-2023)\n\
    12042023    (04-12-2023)\n\n\
    assuming today's date is 5-12-2023, if '3' is given as the no. of days for consistency,\n\
    the program checks the files in dates 04-12-2023, 03-12-2023 and 02-12-2023\n\
    and checks are conducted tomorrow for 05-12-2023, 04-12-2023 and 03-12-2023 and so on.\
    \n\n\n\
    2. Time for sync: Enter the time the program should be triggered everyday to transfer\n\
    The input should be in 24hrs format in hh:mm:ss\
    \n\n\n\
    3. The Password of current user is needed to enable the program to run even when the user is logged out.\n\
    Kindly ensure the user has Admin Priviledges and enter the correct password.\n\n\n\
    4. Mail Notifications Client:- Gives the option to initialize mail notification (Requires a Gmail account). \n\
    Failure updates are also available in the desktop otherwise.\n\n\n\
    5. The App can also use custom date formats. Enter a string separated by spaces using the literals\n\
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
    Thank you for using this program! For more queries, reach out to p.yedukrishna007@gmail.com\
    "
    
    if os.path.exists(PATHS_FILE):         # Get the previously saved paths to show
            prev_paths = decrypt_data(PATHS_FILE)
            SRC = prev_paths[0].strip()
            DEST = prev_paths[1].strip()
            CHKDATES = prev_paths[2]
    else:
        if not os.path.exists(get_local_appdata() + "\\AutomatedDataTransfer"):
            os.mkdir(get_local_appdata() + "\\AutomatedDataTransfer")

    copy2("credentials.json", get_local_appdata() + "\\AutomatedDataTransfer")
            
    layout = [  [sg.Text('Change the Paths')],
                [sg.Text('Source Folder:       '), sg.InputText(SRC), sg.FolderBrowse()],
                [sg.Text('Destination Folder: '), sg.InputText(DEST), sg.FolderBrowse()],
                [sg.Text('No. of days to check for consistency:     '), sg.InputText(CHKDATES, size = (600, 1))],
                [sg.Text('Enter the time for sync:                         '), sg.InputText(time_prompt)],
                [sg.Text('Enter the password for the current user:  '), sg.InputText('', password_char='*')],
                [sg.Text('Enter the date format used (Kindly refer to the Help section):'), sg.InputText(DATE_FORMAT)],
                [sg.Text("(Your Password is not stored by this Program)")],
                [sg.Text()],
                [sg.Button('Ok'), sg.Button('Transfer Now'), sg.Button('Help'), sg.Button('Close')]
             ]

    window = sg.Window('Automated Data Transfer', layout, icon=CUR_DIR + "\\transfer.ico",
                       grab_anywhere = True, size = (750, 300))
    
    sg.popup_scrolled(help_prompt, title="Help", modal=True, size=(100, 10))

    while True:
        event, values = window.read()
        if event  == 'Close' or event == sg.WIN_CLOSED:
            window.close()
            os._exit(0)
        
        elif event == "Help":
            sg.popup_scrolled(help_prompt, title="Help", modal=True, size=(100, 10))
            continue
        
        elif event == "Ok":
            SRC = values[0]
            DEST = values[1]
            CHKDATES = values[2]
            SCH_TIME = values[3]
            PASSWORD = values[4]
            DATE_FORMAT = check_date_format(values[5])
            
            try:
                files = os.listdir(SRC)
            
            except FileNotFoundError:
                sg.popup("Unable to find Source folder or doesn't exist!", title = "Error", modal = True)
                continue

            except ValueError:
                sg.popup("Invalid entry for no. of days! Enter a number!", title = "Error", modal = True)
                continue

            except:
                sg.popup("Unknown Exception has occured!", modal = True, title = "Error")
                continue

            try:
                time_in_format = datetime.strptime(SCH_TIME, "%H:%M:%S")
            
            except:
                sg.popup("Invalid time entered! Enter correct time in format!", title = "Error", modal = True)
                continue

            if not os.path.exists(DEST):
                sg.popup("Unable to find Destination folder or doesn't exist!", title = "Error", modal = True)
                
            elif SRC == DEST:
                sg.popup("Source and Destination are the same folder!", title = "Error")

            elif int(CHKDATES) <= 0:
                sg.popup("Invalid entry for no. of days!", title = "Error", modal = True)
            
            elif len(files) < int(CHKDATES):
                sg.popup("Entered no. of days is more than dates \nin source folder! Try again!", title = "Error", modal = True)
            
            elif DATE_FORMAT == "INVALID DATE FORMAT":
                sg.popup("Invalid Format String for date! Kindly refer to the help page.", title = "Error", modal = True)

            else:
                with open(PATHS_FILE, "wb") as f:
                    f.write(encrypt(SRC + "\n" + DEST + "\n" + CHKDATES + "\n" + DATE_FORMAT + "\n").encode('utf-8'))
                    f.close()
                    status = Create_Task(PASSWORD, time_in_format)

                if status == "SUCCESS":
                    sg.popup("Successfully updated the paths!", title = "Success", modal=True)    

                elif status == "FAILED":
                    sg.popup("Unable to create task! Kindly check the entered password and permissions and Try again!", title = "Failed", modal=True)

                elif status == "MISSING_EXE":
                    sg.popup("Unable to find the required files in installation directory! Try reinstalling the program!", title="Failed Install", modal=True)

                exe_path = CUR_DIR + "\\MailClient.exe"
                result = run([exe_path])
                if result.returncode == 0:
                    sg.popup("Successfully completed setting up the transfer! A confirmation mail will be sent to recipient if credentials are valid")
                else:
                    sg.popup("Unable to initialize the Mail Client.\n \
                            The Task will work as scheduled with failure notifications in the Desktop.", modal=True)

        elif event == "Transfer Now":
            sg.popup("Trying to Transfer files. Kindly Wait after clicking OK.", title = "Transferring", modal = True)
            exe_path = CUR_DIR + "\\TransferPrg.exe"
            result = run([exe_path])
            sg.popup("Completed the transfer!", modal = True)

if __name__ == "__main__":
    if not isUserAdmin():
        print("Re-launching as admin!")
        runAsAdmin()
        os._exit(0)
    else:    
        INIT_PATHS_FILE()
        os._exit(0)