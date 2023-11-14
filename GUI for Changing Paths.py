import PySimpleGUI as sg
import os

sg.theme('DarkAmber')

SRC = ""
DEST = ""
CHKDATES = 1

if os.path.exists("Paths.bin"):         # Get the previously saved paths to show
    with open("Paths.bin", "r") as f:
        prev_paths = f.readlines()            
        SRC = prev_paths[0].strip()
        DEST = prev_paths[1].strip()

layout = [  [sg.Text('Change the Paths')],
            [sg.Text('Source Folder:       '), sg.InputText(SRC, size=(200,1))],
            [sg.Text('Destination Folder: '), sg.InputText(DEST, size=(200,1))],
            [sg.Text('No. of days to check for consistency: '), sg.InputText("1")],
            [sg.Button('Ok'), sg.Button('Close')]
         ]

# Create the Window
window = sg.Window('Automated Data Transfer', layout,
                   grab_anywhere = True, size = (600, 150))

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event in(sg.WIN_CLOSED, 'Close'): # if user closes window or clicks close
        break
    
    SRC = values[0]
    DEST = values[1]
    CHKDATES = values[2]
    
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
            f.write(CHKDATES)
            f.close()

        sg.popup("Successfully updated the paths!", title = "Success")
        
window.close()
