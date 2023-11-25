import email, smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date

def SendLogs(code = 0, details = ""):
    today = date.today()

    try:
        with open("Paths.bin", "r") as f:
            PATHS = f.readlines()
            MAIL_LIST = PATHS[3].strip()
            
    except:
        code = 1

    if code == 0:            
        subject = f"Logs for {today}"
        body = f"Successfully Completed transfer {today}\nLogfiles from Automated Data Transfer Program at SSSIHMS for {today} are attached below"
    else:
        subject = f"Failed to transfer files on {today}"
        if code == 1:
            body = "Unable to read the Paths.bin file!"   
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

    sender_email = ""
    recipients = "" + "," + MAIL_LIST #to add more recipients, continue string by comma and 2nd mail id in same string
    password = ""

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipients
    message["Subject"] = subject

    filename = f"./Logfiles/{today}.log"  # In same directory as script

    # Open PDF file in binary mode
    try:
        
        with open(filename, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )
        
    except:
        body = body + "\n\nError: Unable to find the log file!"

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    # Add attachment to message and convert message to string
    try:
        message.attach(part)
    except:
        message.attach(MIMEText("Unable to locate Logfile", "plain"))
        
    text = message.as_string()

    # Start SMTP server and send mail through the given mail id
    s = smtplib.SMTP('smtp-mail.outlook.com', 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(sender_email, password)
    try:
        s.sendmail(message["From"], message["To"].split(","), text)
    except:
        with open("MailFailed.log", "w") as f:
            f.write(f"Failed to notify through mail!\nCheck your mail id {recipients} \nor run EditPaths program!")
    
    exit(code)


if __name__ == "__main__":
    SendLogs(0)
