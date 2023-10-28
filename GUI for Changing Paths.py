import PySimpleGUI as sg
import os

sg.theme('DarkAmber')

SRC = ""
DEST = ""

if os.path.exists("Paths.bin"):         # Get the previously saved paths to show
    with open("Paths.bin", "r") as f:
        prev_paths = f.readlines()            
        SRC = prev_paths[0].strip()
        DEST = prev_paths[1].strip()


layout = [  [sg.Text('Change the Paths')],
            [sg.Text('Source Folder:       '), sg.InputText(SRC, size=(200,1))],
            [sg.Text('Destination Folder: '), sg.InputText(DEST, size=(200,1))],
            [sg.Button('Ok'), sg.Button('Close')]
         ]

# Create the Window
window = sg.Window('Automated Data Transfer', layout,
                   grab_anywhere = True, size = (600, 125))

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event in(sg.WIN_CLOSED, 'Close'): # if user closes window or clicks close
        break
    
    SRC = values[0]
    DEST = values[1]
    
    if not os.path.exists(SRC): # sanitize
        sg.popup("Source folder doesn't exist!")

    elif not os.path.exists(DEST):
        sg.popup("Destination folder doesn't exist!")

    else:
        with open("Paths.bin", "w") as f:
            f.write(SRC)
            f.write("\n")
            f.write(DEST)
            f.close()

        sg.popup("Successfully updated the paths!")
        
window.close()
