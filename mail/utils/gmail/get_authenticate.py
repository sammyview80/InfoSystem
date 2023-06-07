# import os
# import pickle

# from google.auth.transport.requests import Request
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from googleapiclient.discovery import build
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
# from users.serializers import UserGmailTokenSerializer
# from django.core.files import File


# from pathlib import Path

# BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


# SCOPES = ["https://www.googleapis.com/auth/gmail.readonly",
#           "https://www.googleapis.com/auth/gmail.modify",]


# def save_db(Serializer, userId, credsDir, pickelFile):
#         """This will save the file in the database"""
#         data = {
#             'pickle_token': pickelFile,
#             'credentials': File(open(credsDir, 'rb'), name=os.path.basename(credsDir)),
#             'user': userId
#         }
#         serializer = Serializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#         else:
#             print(serializer.errors)


# def get_authenticate(credentials):
#     """
#         Retun a builded service after authetication
#     """
#     creds = None  
#     print('userin auth', list(credentials)[0])
#     print(BASE_DIR,'idfjidjfij')
#     userId = list(credentials)[0]['user']
#     credsDir = BASE_DIR.joinpath(list(credentials)[0]['credentials'])
#     credsDir = f'{BASE_DIR}{list(credentials)[0]["credentials"]}'
#     print('cird', credsDir)
#     pickleDir = BASE_DIR.joinpath(list(credentials)[0]['pickle_token']) if list(credentials)[0]['pickle_token'] is not None else ''
#     # the file token.pickle stores the user's access and refresh tokens, and is
#     # created automatically when the authorization flow completes for the first time
#     if os.path.exists(pickleDir):
#         with open(pickleDir, "rb") as token:
#             creds = pickle.load(token)
#     # if there are no (valid) credentials availablle, let the user log in.
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 credsDir, SCOPES)
#             creds = flow.run_local_server(port=0)
#         # save the credentials for the next run
#         with open("token.pickle", "wb") as token:
#             save_db(UserGmailTokenSerializer,userId, credsDir, pickle.dump(creds, token))
            
#     return build('gmail', 'v1', credentials=creds)

import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import requests
import tempfile

from pathlib import Path
import json
from users.serializers import UserGmailTokenSerializer
from users.models import UserGmailToken
import io



BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly",
          "https://www.googleapis.com/auth/gmail.modify",]


def get_data_from_url(url):
    try: 
        response = requests.get(url)
        print('response', response.status_code)
        if response is not None:
            if response.status_code == 200:
                return response
    except Exception as e:
        return None


def get_authenticate(credientials):
    """
        Retun a builded service after authetication
    """
    creds = None  
    print('file', credientials)
    userId = list(credientials)[0]['user']
    file_content = get_data_from_url(f'http://localhost:8000{list(credientials)[0]["credentials"]}')
    pickle_content = get_data_from_url(f'http://localhost:8000{list(credientials)[0]["pickle_token"]}')
    pickle_file = None
    creds_file = None
    authorization_url=None

    if pickle_content is not None:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(pickle_content.content)
                temp_file.flush()
                pickle_file = temp_file
                with open(temp_file.name, 'rb') as temp_file:
                    creds = pickle.load(temp_file)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(file_content.content)
                temp_file.flush()
                flow = InstalledAppFlow.from_client_secrets_file(temp_file.name, SCOPES
                )
                authorization_url, _ = flow.authorization_url(prompt='consent')
                # print('Please go to this URL: {}'.format(authorization_url))
                creds = flow.run_local_server(port=0)
                with open(temp_file.name, "wb") as token:
                    instance = UserGmailToken.objects.get(user=userId)
                    print('instance', instance)
                    # data = {
                    #     'pickle_token': pickle.dump(creds, token),
                    #     'credentials': temp_file,
                    #     'user': userId
                    # }
                    # Create a file-like object using io.BytesIO()
                    pickle_file = io.BytesIO()

                    # Dump the `creds` object into the file-like object
                    pickle.dump(creds, pickle_file)

                    # Set the position of the file-like object to the beginning
                    pickle_file.seek(0)

                    # Assign the file-like object to the `pickle_token` field
                    instance.pickle_token.save('pickle_token.pkl', pickle_file)

                    # Save the changes to the database
                    instance.save()

                # if serializer.is_valid():
                #     # Save the changes to the database
                #     serializer.save()
    print('creds', creds)
    return build('gmail', 'v1 ', credentials=creds)
