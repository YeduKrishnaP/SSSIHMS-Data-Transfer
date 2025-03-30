import os
import base64
from datetime import date, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

from userpaths import get_local_appdata, get_desktop
from Encryption import decrypt_data

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def log_error(message):
        message = str(datetime.now()) + ":\t" + message
        print(message)
        with open(get_desktop() + "\\ADTFailed.txt", "a") as adt:
            adt.write(f"{message}\n")

def get_gmail_service(base_path):
    """
    Authenticate and get Gmail service using OAuth 2.0
    """
    creds = None
    token_path = base_path + "/token.json"
    credentials_path = base_path + "/credentials.json"

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    os.makedirs(os.path.dirname(token_path), exist_ok=True)
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except Exception as e:
            print(f"Error loading existing credentials: {e}")
            log_error(f"Error loading existing credentials: {e}")
            creds = None

    if not creds or not creds.valid:
        try:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server()
            
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
                
        except Exception as e:
            print(f"Authentication error: {e}")
            log_error(f"Authentication error: {e}")
            return None

    return build('gmail', 'v1', credentials=creds)

def create_message(sender, recipients, subject, body, attachment_path=None):
    """
    Create a message for Gmail API with optional file attachment
    
    Args:
    - sender: Sender's email address
    - recipients: Comma-separated string of recipient email addresses
    - subject: Email subject
    - body: Email body
    - attachment_path: Optional path to file to be attached
    """
    if isinstance(recipients, str):
        recipients = [r.strip() for r in recipients.split(',')]
    
    if not recipients:
        log_error("At least one recipient email address is required")
        # raise ValueError("At least one recipient email address is required") Dont raise error as it will break the execution flow
        return

    message = MIMEMultipart()
    message['to'] = ', '.join(recipients)  # Join multiple recipients
    message['from'] = sender
    message['subject'] = subject
    msg = MIMEText(body)
    message.attach(msg)

    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, 'rb') as file:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(file.read())
        
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(attachment_path)}"')
        message.attach(part)

    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def SendLogs(code=0, details=""):
    """
    Send logs using Gmail API with OAuth 2.0
    """
    today = date.today()
    docs_path = get_local_appdata() + "\\AutomatedDataTransfer"
    PATHS_FILE = docs_path + "\\Paths.adt"
    LOGS_PATH = f"{docs_path}\\Logfiles\\{today}.log"

    try:
        DATA = decrypt_data(PATHS_FILE)
        sender_email = None
        recipients = None
        
        # print("Decrypted DATA:", DATA)
        # print("DATA Length:", len(DATA))

        if len(DATA) == 7:
            sender_email = DATA[4]
            recipients = DATA[6].split(',')
            recipients = [r.strip() for r in recipients if r.strip()]
        
        if not sender_email:
            log_error("Sender email is empty")
            return
            # raise ValueError("Sender email is empty")
        
        if not recipients:
            log_error("No recipient emails found")
            return
            # raise ValueError("No recipient emails found")
        
        recipients_str = ', '.join(recipients)
    except Exception as e:
        log_error(f"Error reading paths: {e}")
        os._exit(1)

    if code == 0: #Succesful tranfer
        subject = f"Logs for {today}"
        body = f"Successfully Completed transfer {today}\nLogfiles from Automated Data Transfer Program are attached."

    elif code == -1: #Code for init of the client
        subject = "AutomatedDataTransfer Email Client Test"
        body = f"""Test Email from Automated Data Transfer

This is a test email sent from the Automated Data Transfer application.

Sender: {sender_email}
Recipients: {recipients_str}
Timestamp: {today}

Thank you for using the Automated Data Transfer app!

Regards,
Automated Data Transfer Team"""
        
    else:
        subject = f"Failed to transfer files on {today}"
        body = "Transfer failed. Check logs for details."
        log_error(f"{subject}\n{body}")

    try:
        service = get_gmail_service(docs_path)
        
        if not os.path.exists(LOGS_PATH) and code!=-1:
            body += "\n\nNote: Log file not found at expected location."
            LOGS_PATH = None
        
        message = create_message(
            sender_email, 
            recipients_str, 
            subject, 
            body,
            attachment_path=LOGS_PATH
        )

        try:
            result = service.users().messages().send(userId='me', body=message).execute()
            print("Email sent successfully")
            print("Message ID:", result.get('id'))
        except Exception as e:
            log_error(f"Error sending email: {e}")

    except Exception as e:
        log_error(f"OAuth or Email Error: {e}")        
    return 

if __name__ == "__main__":
    SendLogs(-1)