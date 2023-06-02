import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from users.serializers import UserGmailTokenSerializer
from django.core.files import File


from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly",
          "https://www.googleapis.com/auth/gmail.modify",]


def save_db(Serializer, userId, credsDir, pickelFile):
        """This will save the file in the database"""
        data = {
            'pickle_token': pickelFile,
            'credentials': File(open(credsDir, 'rb'), name=os.path.basename(credsDir)),
            'user': userId
        }
        serializer = Serializer(data=data)
        if serializer.is_valid():
            serializer.save()
        else:
            print(serializer.errors)


def get_authenticate(credentials):
    """
        Retun a builded service after authetication
    """
    creds = None  
    print('userin auth', list(credentials)[0])
    print(BASE_DIR,'idfjidjfij')
    userId = list(credentials)[0]['user']
    credsDir = BASE_DIR.joinpath(list(credentials)[0]['credentials'])
    credsDir = f'{BASE_DIR}{list(credentials)[0]["credentials"]}'
    print('cird', credsDir)
    pickleDir = BASE_DIR.joinpath(list(credentials)[0]['pickle_token']) if list(credentials)[0]['pickle_token'] is not None else ''
    # the file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists(pickleDir):
        with open(pickleDir, "rb") as token:
            creds = pickle.load(token)
    # if there are no (valid) credentials availablle, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credsDir, SCOPES)
            creds = flow.run_local_server(port=0)
        # save the credentials for the next run
        with open("token.pickle", "wb") as token:
            save_db(UserGmailTokenSerializer,userId, credsDir, pickle.dump(creds, token))
            
    return build('gmail', 'v1', credentials=creds)
