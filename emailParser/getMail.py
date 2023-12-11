#ACCESSING GMAIL FROM A HEADLESS ENVIORNMENT REQUIRES CHANGES IN GOOGLE ACCOUNT SETTINGS AND CONFIGURATION OF GOOGLE API

from __future__ import print_function
import os.path
import base64
import email
import re
#from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

# Set up logging
#logging.basicConfig(filename='/home/pi/Documents/app.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')


def get_email_data():
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

    def get_text_plain_email_content(msg):
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    return part.get_payload(decode=True).decode('utf-8')
        else:
            if msg.get_content_type() == 'text/plain':
                return msg.get_payload(decode=True).decode('utf-8')
        return None
    
    """ 
    EXAMPLE BRYX DISPATCH EMAIL CONTENTS: 
    dispatch: 800
    location: 100 MAIN RD
    crossStreets: FIRST ST / SECOND ST
    city: ALBERTSON
    state: ny
    box: 80-NW
    callType: Automatic Alarm
    category: info
    narrative: 1st flr smoke det
    coordinates: [-69.64518823333333, 420.774188466666665]
    incidentId: 2022-00000354
    cadId: 444
    timestamp: 2022-11-11 00:05:34.623000+00:00 
    """
    #parse_email_content will pull out relevant information from the email
    def parse_email_content(content):
        lines = content.splitlines()
        location = cross_streets = category = None
        for line in lines:
            if line.startswith("location:"):
                location = re.sub(r'^\d+\s+', '', line[9:].strip())
            elif line.startswith("crossStreets:"):
                cross_streets = [street.strip() for street in line[13:].split('/')]
            elif line.startswith("category:"):
                category = line[9:].strip()
        return location, cross_streets, category

    creds = None
    #check if token to acess GMAIL API is available at specified file path
    if os.path.exists('/home/pi/Documents/token.json'):
        creds = Credentials.from_authorized_user_file('/home/pi/Documents/token.json', SCOPES)
    #If credentials are expired or do not exist at that file path they CAN be generated with valid login credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '/home/pi/Documents/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('/home/pi/Documents/token.json', 'w') as token:
            token.write(creds.to_json())

    #To allow this method of accessing GMAIl to work, the account must be configured for external IMAP access
    #valid tokens can be generated on any device logged into the desired google account and copied over to the raspberry pi
    #HOWEVER tokens do EXPIRE after a certain period of time and this would require constant manual updates
    #BY giving the raspberry pi credentials to login to the gmail account continually, new tokens can be constantly created
    #this requires an APP PASSWORD to be created which allows devices that dont supprt 2 factor authentication to login a google account

    try:
        service = build('gmail', 'v1', credentials=creds)
        query = "from:no-reply@bryx.com is:unread"
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])

        if not messages:
            #logging.info('No new messages found.')
            return None, None, None
        else:
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id'], format='raw').execute()
                msg_str = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
                mime_msg = email.message_from_bytes(msg_str)
                content = get_text_plain_email_content(mime_msg)
                if content:
                    location, cross_streets, category = parse_email_content(content)
                    service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()
                    #logging.info('Email processed successfully.')
                    return location, cross_streets, category
                else:
                    logging.warning('No content found in the email.')
                    return None, None, None
    except HttpError as error:
        #logging.error(f'An error occurred: {error}')
        return None, None, None
    
def main():
    location,cross_streets,category = get_email_data()
    print(f'{location}\n{cross_streets}\n{category}\n')

if __name__ == '__main__':
    main()
