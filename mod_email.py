# Module with modifying functions for email services

import base64
import mimetypes
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup

#
# Create a new message that can be sent via email
def create_msg(sender, to, subject, msg_text):
    try:
        msg = MIMEText(msg_text)
        msg['to'] = to
        msg['from'] = sender
        msg['subject'] = subject
        raw_msg = base64.urlsafe_b64encode(msg.as_string().encode("utf-8"))
        return { 'raw': raw_msg.decode("utf-8") }
    except Exception as e:
        print("An error occurred: %s" % e)
        return None


#
# Create a new message with an attachment
def create_msg_w_att(sender, to, subject, msg_text, file):
    try:
        msg_body = MIMEText(msg_text)
        msg = MIMEMultipart()
        msg['to'] = to
        msg['from'] = sender
        msg['subject'] = subject
        msg.attach(msg_body)
        content_type, encoding = mimetypes.guess_type(file)

        # If the file's MIME type can not be guessed or if it's encoded, 
        # default to a generic type for binary data
        if content_type is None or encoding is not None:
            content_type = "application/octet-stream"

        # Split the MIME type into its main and sub types
        main_type, sub_type = content_type.split("/", 1)

        # If file type is text, create a MIMEText object
        if main_type == "text":
            with open(file, 'rb') as fp:
                mime = MIMEText(fp.read().decode("utf-8"), _subtype=sub_type)
        # If file type is image, create a MIMEImage object
        elif main_type == "image":
            with open(file, 'rb') as fp:
                mime = MIMEImage(fp.read(), _subtype=sub_type)
        # For all other file types, create a MIMEBase object
        else:
            with open(file, 'rb') as fp:
                mime = MIMEBase(main_type, sub_type)
                mime.set_payload(fp.read())

        mime.add_header("Content-Disposition", "attachment", filename=file)
        msg.attach(mime)
        raw_msg = base64.urlsafe_b64encode(msg.as_string().encode("utf-8"))
        return { 'raw': raw_msg.decode("utf-8") }
    except Exception as e:
        print("An error occurred: %s" % e)
        return None


#
# Create a new draft email with given raw message
def create_draft(service, user_id, msg_body):
    try:
        msg = {'message': msg_body}
        service.users().drafts().create(userId=user_id, body=msg).execute()
    except Exception as e:
        print("An error occurred: %s" % e)
        return None


#
# Send an email with given raw message
def send_email(service, user_id, msg):
    try:
        message = service.users().messages().send(userId=user_id, body=msg).execute()
        print("Message ID = %s" % message['id'])
    except Exception as e:
        print("An error occurred: %s" % e)
        return None


#
# Get a specific email using its message ID
def get_email(service, user_id, msg_id):
    try:
        # Get message and create a temporary dictionary to store information
        msg = service.users().messages().get(userId=user_id, id=msg_id).execute()
        temp = {'From': '', 'Date': '', 'Subject': '', 'Message Body': '', 'Attachment': 'None'}
        
        payload = msg['payload']
        headers = payload['headers']

        # Get information from headers
        for header in headers:
            if header['name'] == 'From': # Get sender
                temp['From'] = header['value']
            if header['name'] == 'Date': # Get date
                temp['Date'] = header['value']
            if header['name'] == 'Subject': # Get subject
                temp['Subject'] = header['value']
        
        parts = payload.get('parts', [])
        msg_body = ""

        # Search parts for attachments, text, or multipart
        for part in parts:
            body = part['body']
            
            if part['filename']: 
                # Get attachment ID and filename
                att_id = body['attachmentId']
                filename = part['filename']
                
                att = service.users().messages().attachments().get(userId=user_id, messageId=id, id=att_id).execute()
                att_data = att['data']
                file_data = base64.urlsafe_b64decode(att_data.encode('utf-8'))
                
                # Download attachment to current directory as filename
                with open(filename, 'wb') as f:
                    f.write(file_data)
                temp['Attachment'] = filename
            
            # Get body text either as plain or html
            elif part['mimeType'] == ('text/plain' or 'text/html'):
                data = body['data']
                if data:
                    msg_body += base64.urlsafe_b64decode(data).decode('utf-8')
            
            elif part['mimeType'] == 'multipart/alternative':
                for subpart in part['parts']: # Get subparts
                    body = subpart['body']
                    # Get body text either as plain or html
                    if subpart['mimeType'] == ('text/plain' or 'text/html'):
                        data = body['data']
                        if data: msg_body += base64.urlsafe_b64decode(data).decode('utf-8')
            # Convert any html in final message body and put it in temp
            soup = BeautifulSoup(msg_body, 'html.parser')
            temp['Message Body'] = soup.get_text() 
                
        # Print everything in temp with specific formating for different items
        for item, value in temp.items():
            if item == 'Message Body':
                print(f"{item}: \n{value}")
            elif item == 'Attachment':
                print(f"{item}: {value}\n")
            else:
                print(f"{item}: {value}")
    except Exception as e:
        print("An error occurred: %s" % e)


#
# List all unread emails in primary inbox and mark them as read
def read_unread_emails(service, user_id):
    try:
        # Make a list containing every unread message in primary
        unread_msgs = service.users().messages().list(userId=user_id, labelIds=["INBOX", "UNREAD"]).execute()
        msg_list = unread_msgs.get('messages', [])
        print("Total unread messages in inbox: %d\n" % len(msg_list))
        if len(msg_list) > 0:
            for message in msg_list:
                # Create a temporary dictionary to store information
                temp = {'From': '', 'Date': '', 'Subject': '', 'Message Body': '', 'Attachment': 'None'}
                
                # Use message ID to get message as well as its payload and header
                id = message['id']
                msg = service.users().messages().get(userId=user_id, id=id).execute()
                payload = msg['payload']
                headers = payload['headers']

                # Get information from headers
                for header in headers:
                    if header['name'] == 'From': # Get sender
                        temp['From'] = header['value']
                    if header['name'] == 'Date': # Get date
                        temp['Date'] = header['value']
                    if header['name'] == 'Subject': # Get subject
                        temp['Subject'] = header['value']
                parts = payload.get('parts', [])
                msg_body = ""

                # Search parts for attachments, text, or multipart
                for part in parts:
                    body = part['body']
                    
                    if part['filename']: 
                        # Get attachment ID and filename
                        att_id = body['attachmentId']
                        filename = part['filename']
                        
                        att = service.users().messages().attachments().get(userId=user_id, messageId=id, id=att_id).execute()
                        att_data = att['data']
                        file_data = base64.urlsafe_b64decode(att_data.encode('utf-8'))
                        # Download attachment to current directory as filename
                        with open(filename, 'wb') as f:
                            f.write(file_data)
                        temp['Attachment'] = filename
                    
                    # Get body text either as plain or html
                    elif part['mimeType'] == ('text/plain' or 'text/html'): # Store text in message body
                        data = body['data']
                        if data:
                            msg_body += base64.urlsafe_b64decode(data).decode('utf-8')
                    
                    elif part['mimeType'] == 'multipart/alternative':
                        for subpart in part['parts']: # Get subparts
                            body = subpart['body']
                            # Get body text either as plain or html
                            if subpart['mimeType'] == ('text/plain' or 'text/html'): # Store text in message body
                                data = body['data']
                                if data: msg_body += base64.urlsafe_b64decode(data).decode('utf-8')
                    # Convert any html in final message body and put it in temp
                    soup = BeautifulSoup(msg_body, 'html.parser')
                    temp['Message Body'] = soup.get_text() 

                # Mark emails as read
                msg = service.users().messages().modify(userId=user_id, id=id, body={'removeLabelIds': ["UNREAD"]}).execute()
                
                # Print everything in temp with specific formating for different items
                for item, value in temp.items():
                    if item == 'Message Body':
                        print(f"{item}: \n{value}")
                    elif item == 'Attachment':
                        print(f"{item}: {value}\n")
                    else:
                        print(f"{item}: {value}")

    except Exception as e:
        print("An error occurred: %s" % e)
