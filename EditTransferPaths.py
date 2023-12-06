import PySimpleGUI as sg
import os
import subprocess
import win32com.client

def Create_Task(user_password):

    cur_user = os.getlogin()
    computer_name = os.environ['COMPUTERNAME']
    cur_dir = os.getcwd()
    sch_file = cur_dir + "\\" + "ScheduleThis.bat"

    SCH = win32com.client.Dispatch('Schedule.Service')
    SCH.Connect()
    root = SCH.GetFolder('\\')

    TASK = SCH.NewTask(0)

    #Define Trigger properties
    TriggerType = 2 #Daily
    trigger = TASK.Triggers.Create(TriggerType)
    starttime = "2023-12-04T14:30:00"   #yyyy-mm-ddThh-mm-ss
    trigger.StartBoundary = starttime
    trigger.DaysInterval = 1
    trigger.Enabled = True
    trigger.Id = "DailyTrigger"

    #Define Actions of task
    action = TASK.Actions.Create(0) # 0 refers to the type execute
    action.Path = "cmd.exe"
    action.Arguments = f'/c start "" {sch_file}'
    action.ID = "ADTTestPywin32"
    action.WorkingDirectory = cur_dir

    #Addtnl task info
    TASK.RegistrationInfo.Description = "Testing ADT scheduling using pywin32"
    TASK.Settings.Enabled = True
    TASK.Settings.StopIfGoingOnBatteries = False
    task_create_or_update = 6
    task_logon_none = 1
    TASK.Principal.UserId = cur_user
    TASK.Principal.LogonType = 6

    root.RegisterTaskDefinition(
        "ADTTestPywin32",
        TASK,
        task_create_or_update,
        f"{computer_name}\\{cur_user}",
        user_password,
        task_logon_none
        )


def INIT_PATHS_FILE():
    """
    Function that creates a file to store the paths of the Source and Destination
    folders for the Automated Backup Program to read

    Libraries used: PySimpleGUI, OS
    """    
    sg.theme('Topanga')

    SRC = ""
    DEST = ""
    datesprompt = "(eg: 3 means the program checks 3 previous days for consistency)"
    mailprompt = "Use commas to add multiple Email IDs (eg: xyz@abc.com,abc@xyz.com)"
    
    
    if os.path.exists("Paths.bin"):         # Get the previously saved paths to show
        with open("Paths.bin", "r") as f:
            prev_paths = f.readlines()            
            SRC = prev_paths[0].strip()
            DEST = prev_paths[1].strip()


    layout = [  [sg.Text('Change the Paths')],
                [sg.Text('Source Folder:       '), sg.InputText(SRC), sg.FolderBrowse()],
                [sg.Text('Destination Folder: '), sg.InputText(DEST), sg.FolderBrowse()],
                [sg.Text('No. of days to check for consistency: '), sg.InputText(datesprompt, size = (600, 1))],
                [sg.Text('Enter your email to receive notifications: '), sg.InputText(mailprompt, size = (675, 1))],
                [sg.Text('Enter the password for the current user: '), sg.InputText("Your Password is not stored anywhere by this program")],
                [sg.Button('Ok'), sg.Button('Transfer Now'), sg.Button('Close')]
             ]

    # Create the Window
    window = sg.Window('Automated Data Transfer', layout,
                       grab_anywhere = True, size = (750, 200))

    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event in(sg.WIN_CLOSED, 'Close'): # if user closes window or clicks close
            window.close()
            return 0

        SRC = values[0]
        DEST = values[1]
        CHKDATES = values[2]
        MAIL_LIST = values[3]
        PASSWORD = values[4]
         
        try:
            files = os.listdir(SRC)
            CHKDATES = int(CHKDATES)
        except FileNotFoundError:
            sg.popup("Unable to find Source folder or doesn't exist!", title = "Error", modal = True)
            continue

        except ValueError:
            sg.popup("Invalid entry for no. of days! Enter a number!", title = "Error", modal = True)
            continue

        except:
            continue

        if not os.path.exists(DEST):
            sg.popup("Unable to find Destination folder or doesn't exist!", title = "Error", modal = True)
            
        elif SRC == DEST:
            sg.popup("Source and Destination are the same folder!", title = "Error")

        elif int(CHKDATES) <= 0:
            sg.popup("Invalid entry for no. of days!", title = "Error", modal = True)
        
        elif len(files) < int(CHKDATES):
            sg.popup("Entered no. of days is more than dates \nin source folder! Try again!", title = "Error", modal = True)
            
        elif MAIL_LIST == mailprompt or MAIL_LIST == '':
            sg.popup("Kindly enter the mail id for receiving notifications", title = "Mail Error", modal = True)

        else:
            with open("Paths.bin", "w") as f:
                f.write(SRC)
                f.write("\n")
                f.write(DEST)
                f.write("\n")
                f.write(str(CHKDATES))
                f.write("\n")
                f.write(MAIL_LIST)
                f.close()
                Create_Task(PASSWORD)
            
            if event == 'Transfer Now':
                sg.popup("Kindly Wait! Transferring files!", title = "Transferring", modal = True)
                exe_path = os.getcwd() + "\TransferPrg.exe"
                subprocess.call(exe_path, shell=True)
            sg.popup("Successfully updated the paths!", title = "Success")    

if __name__ == "__main__":
    INIT_PATHS_FILE()

