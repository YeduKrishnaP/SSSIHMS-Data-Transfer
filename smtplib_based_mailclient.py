"""
Old version of the Mail Client that uses the SMTP Library to send mails via google or outlook
(Outdated and doesnt work with Gmail anymore)
"""


import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date
import os
from userpaths import get_local_appdata, get_desktop
from Encryption import decrypt_data

def SendLogs(code = 0, details = ""):   #Function to send mail notification to the user
    """
    Doc here
    """
    today = date.today()
    docs_path = get_local_appdata() + "\\AutomatedDataTransfer"
    PATHS_FILE = docs_path + "\\Paths.adt"
    LOGS_PATH = f"{docs_path}\\Logfiles\\{today}.log"  # In local appdata directory as script
    kill = 0

    try:
            DATA = decrypt_data(PATHS_FILE)
            print(DATA)
            sender_email = DATA[4]
            password = DATA[5]
            recipients = DATA[6] #to add more recipients, continue string by comma and 2nd mail id in same string
            
    except IndexError:
        kill=1

    except:
        code = 1

    if code == 0:            
        subject = f"Logs for {today}"
        body = f"Successfully Completed transfer {today}\nLogfiles from Automated Data Transfer Program at SSSIHMS for {today} are attached below"

    elif code == -1:
        subject = f"AutomatedDataTransfer Email Client"
        body = \
            f"Hello there,\n\n\
Thank you for using AutomatedDataTransfer app developed by Department of Mathematics and Computer Science, Sri Sathya Sai Institute of Higher Learning(Prasanthi Nilayam).\n\n\
This mail is to inform that the Email facility of the ADT app has been succesfully initialized and you will be recieving mails daily regarding the updates of the app.\n\
Have a great day!\n\nRegards,\nYedu Krishna P\nDMACS, SSSIHL(PSN)"    
    else:
        subject = f"Failed to transfer files on {today}"
        if code == 1:
            body = "Unable to read the Paths.dat file!"   
        elif code == 2:
            body = ""
        elif code == 3:
            body = "Unable to find a Source folder"
        elif code == 4:
            body = f"Unable to create target folder {details}"
        elif code == 5:
            body = f"shutil.copy2 failed on file {details}"
        else:
            body = "Unknown  Error Code!"
        
        with open(get_desktop() + "\\ADTFailed.txt", "a") as adt:
            adt.write(subject + "\n" + body + "\n" + details +"\n\n")
    
    if kill ==  1:
        print("killed")
        os._exit(1)

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipients
    message["Subject"] = subject
    
    try:
        if code != -1:
            with open(LOGS_PATH, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())  
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename= {LOGS_PATH}",)
            
    except:
        body = body + "\n\nError: Unable to find the log file!"
    message.attach(MIMEText(body, "plain"))

    if code != -1:
        try:
            message.attach(part)
        except:
            message.attach(MIMEText("Unable to locate Logfile", "plain"))
        
    if not os.path.exists(docs_path + "\\Logfiles\\"):
        os.mkdir(docs_path + "\\Logfiles\\")
        
    with open(docs_path + "\\Logfiles\\MailLogs.txt", "a") as f:
        try:
            s = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10) # 'smtp-mail.outlook.com | smtp.gmail.com'
            s.ehlo()
            f.write(f"Connection established {today}\n")
            s.login(sender_email, password)
            s.send_message(message)
            s.quit()
        
        except smtplib.SMTPException as e:
            print(e)
            f.write(f"Failed to notify through mail!\n\n" + str(e) + "\n")

        except Exception as e:
            print(e)
            f.write(f"Failed to notify through mail! {today}\nCheck your mail id {recipients} \nor run EditPaths program!\n" + str(e) + "\n")

    os._exit(0)

if __name__ == "__main__":
    SendLogs(-1)