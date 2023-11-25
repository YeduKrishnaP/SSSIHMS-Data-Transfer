import PySimpleGUI as sg
import os

def INIT_PATHS_FILE():
    """
    Function that creates a file to store the paths of the Source and Destination
    folders for the Automated Backup Program to read

        
    
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
                [sg.Button('Ok'), sg.Button('Close')]
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

        try:
            CHKDATES = int(CHKDATES)
        except ValueError:
            sg.popup("Invalid entry for no. of days! Enter a number!", title = "Error", modal = True)
            continue

        if MAIL_LIST == mailprompt:
            sg.popup("Kindly enter the mail id for receiving notifications", title = "Mail Error", modal = True)
            continue
        
        
        try:
            files = os.listdir(SRC)
        except FileNotFoundError:
            sg.popup("Unable to find Source folder or doesn't exist!", title = "Error", modal = True)
            continue

        if not os.path.exists(DEST):
            sg.popup("Unable to find Destination folder or doesn't exist!", title = "Error", modal = True)
            
        elif SRC == DEST:
            sg.popup("Source and Destination are the same folder!", title = "Error")

        elif int(CHKDATES) <= 0:
            sg.popup("Invalid entry for no. of days!", title = "Error", modal = True)
        
        elif len(files) < int(CHKDATES):
            sg.popup("Entered no. of days is more than dates \nin source folder! Try again!", title = "Error", modal = True)

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

            sg.popup("Successfully updated the paths!", title = "Success")
    window.close()

if __name__ == "__main__":
    INIT_PATHS_FILE()
