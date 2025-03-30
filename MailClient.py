import PySimpleGUI as sg
import os
from userpaths import get_local_appdata
from Encryption import encrypt, decrypt_data
from EmailClient import SendLogs

def create_mail_data():

    sg.theme('SystemDefault')
    PATHS_FILE = get_local_appdata() + "\\AutomatedDataTransfer\\Paths.adt" # encrypted dat file
    help_prompt = \
    "Welcome to the ADT MailClient help page!\
    \n\n\
    1. This MailClient is used to initialize the Mail Notifications feature which sends notifications to\n\
    specified mail IDs after everyday's transfer. If not provided with any mail ID and password for sender or recipient mail IDs,\n\
    The failure notifications are automatically displayed in a text file in the Desktop.\n\n\n\
    2. For using this feature, you need to have a valid GMAIL address. The app will require you to login only this once.\n\" \
    Incase of mail failure, kindly restart the AutomatedDataTransfer program and re-enter the mail credentials.\n\
    \n\n\nThank you for using this program! For more queries, reach out to p.yedukrishna007@gmail.com\
    "

    if not os.path.exists(get_local_appdata() + "\\AutomatedDataTransfer"):
        os.mkdir(get_local_appdata() + "\\AutomatedDataTransfer")
            
    layout = [  [sg.Text('Initialize Mail Client')],
                [sg.Text('Sender GMail ID:            '), sg.InputText('Valid Gmail ID with configurations (See Help)')],
                # [sg.Text('Sender GMail password: '), sg.InputText('', password_char='*')],
                [sg.Text('Mail Recipients:             '), sg.InputText("Use commas to add multiple Email IDs (eg: xyz@abc.com,abc@xyz.com)", size = (600, 1))],
                [sg.Text()],
                [sg.Button('Ok'), sg.Button('Help'), sg.Button('Return')]
             ]

    window = sg.Window('ADT Mail Client', layout, icon= os.getcwd() + "\\transfer.ico", grab_anywhere = True, size = (750, 170))

    while True:
        event, values = window.read()
        if event  == 'Return' or event == sg.WIN_CLOSED: 
            window.close()
            os._exit(0)
        
        elif event == "Help":
            sg.popup_scrolled(help_prompt, title="Help", modal=True, size=(100, 10))
            continue
        
        elif event == "Ok":
            SENDER_MAIL = values[0]
            PASSWORD = "DEPRECATED!!! USING Google OAUTH now!"
            MAIL_LIST = values[1]

            try:
                DATA = decrypt_data(PATHS_FILE)
                if(len(DATA) == 4):
                    DATA.append(SENDER_MAIL)
                    DATA.append(PASSWORD)
                    DATA.append(MAIL_LIST)

                elif(len(DATA) == 7):
                    DATA[4] = SENDER_MAIL
                    DATA[5] = PASSWORD
                    DATA[6] = MAIL_LIST

                else:
                    sg.popup("Empty Paths.adt file detected!\nPlease raise an issue at https://github.com/YeduKrishnaP/SSSIHMS-Data-Transfer to report the issue.")
                    return

                out = ""
                for i in DATA:
                    out += i + "\n"
                with open(PATHS_FILE, "wb") as f:
                    f.write(encrypt(out).encode('utf-8'))
                sg.popup("Trying to send test mail. Kindly Wait after clicking OK")
                SendLogs(-1)
                return

            except FileNotFoundError:
                sg.popup("Unable to find Paths.adt file or doesn't exist!\n(Run the AutomatedDataTransfer program first)", title = "Error", modal = True)
                continue

if __name__ == "__main__":
    create_mail_data()