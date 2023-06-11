from google.auth.transport.requests import Request
import pickle
import io
import tempfile
import requests
from google_auth_oauthlib.flow import InstalledAppFlow
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from .serializers import UserSerializer, UserGmailTokenSerializer
# from fileManager.mail.main import FetchMail, CheckMail
from mail.main import FetchMail, CheckMail
from django.contrib.auth import authenticate, login
import asyncio
import threading
from .models import CustomUser, UserGmailToken
from django.shortcuts import get_object_or_404
from mail.utils.gmail.get_authenticate import get_data_from_url, get_authenticate
from google.oauth2.credentials import Credentials
import pandas as pd
import numpy as np
from routine.models import Day, BatchSemester, Room, Group, TeacherWithSubject, Routine
from routine.serializers import DaySerializer, BatchSemesterSerializer, RoomSerializer, GroupSerializer, PeriodSeriallizer, TeacherWithSubjectSerializer, RoutineSerializer
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly",
          "https://www.googleapis.com/auth/gmail.modify"]


class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if email is None or password is None:
            return Response("Email and password are required fields.", status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return Response("User successfully logged in.", status=status.HTTP_200_OK)
        else:
            return Response("Invalid email or password.", status=status.HTTP_401_UNAUTHORIZED)


class UserDetailView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserUpdateView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user  # Assuming the user is authenticated
        data = request.data

        # Update the user fields with the provided data
        user.email = data.get('email', user.email)
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)

        if data.get('password', user.password):
            user.set_password(data.get('password'))

        # Save the updated user
        user.save()

        return Response("User successfully updated")


class FetchMailView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def fetch_mail(self, user, creds):
        # Implement your email fetching logic here
        FetchMail(user, creds).run()

    def save_file(self, user):
        CheckMail(user).run()

    def post(self, request):
        email = request.user
        user = CustomUser.objects.filter(email=email).values().first()
        credientials = UserGmailToken.objects.filter(user=email)
        serializerCreds = UserGmailTokenSerializer(credientials, many=True)

        # Run the email fetching operation in a separate thread
        thread = threading.Thread(
            target=self.fetch_mail, args=(user, serializerCreds.data,))
        thread.start()

        thread.join()

        thread = threading.Thread(target=self.save_file, args=(user,))
        thread.start()

        thread.join()

        return Response("Email fetching started.", status=200)


class OauthLink(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        email = request.user
        user = CustomUser.objects.filter(email=email).values().first()
        print('user', user)
        instance = UserGmailToken.objects.filter(user=email)
        print('instance', instance)
        credentials = UserGmailTokenSerializer(instance, many=True)
        file_content = get_data_from_url(
            f'http://localhost:8000{list(credentials.data)[0]["credentials"]}')
        # pickle_content = get_data_from_url(f'http://localhost:8000{list(credentials.data)[0]["pickle_token"]}')
        authorization_url = None
        scheme = request.scheme
        host = request.get_host()
        base_url = f"{scheme}://{host}"
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file_content.content)
            temp_file.flush()
            flow = InstalledAppFlow.from_client_secrets_file(
                temp_file.name, SCOPES, redirect_uri=f'{base_url}/users/oauth2callback/?user={email}')
            authorization_url, _ = flow.authorization_url(prompt='consent')

        return Response({"outhlink": authorization_url}, status=status.HTTP_201_CREATED)


class CatchOauthCreds(APIView):

    def get(self, request):
        authorization_code = request.GET.get('code')
        email = request.GET.get('user')
        print(email)
        state = request.GET.get('state')
        user = CustomUser.objects.filter(email=email).values().first()
        print('user', user)

        instance = UserGmailToken.objects.filter(user=user['id'])
        credentials = UserGmailTokenSerializer(instance, many=True)
        scheme = request.scheme
        host = request.get_host()
        base_url = f"{scheme}://{host}"

        file_content = get_data_from_url(
            f'{base_url}{list(credentials.data)[0]["credentials"]}')
        # pickle_content = get_data_from_url(f'http://localhost:8000{list(credentials.data)[0]["pickle_token"]}')
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file_content.content)
            temp_file.flush()
            flow = InstalledAppFlow.from_client_secrets_file(
                temp_file.name, SCOPES, redirect_uri=f'{base_url}/users/oauth2callback/?user={email}')
            credentials = flow.fetch_token(code=authorization_code)
            credentials = Credentials(credentials)
            with open(temp_file.name, "wb") as token:
                instance = UserGmailToken.objects.get(user=user['id'])
                print('instance', instance)
                # data = {
                #     'pickle_token': pickle.dump(creds, token),
                #     'credentials': temp_file,
                #     'user': userId
                # }
                # Create a file-like object using io.BytesIO()
                pickle_file = io.BytesIO()

                # Dump the `creds` object into the file-like object
                pickle.dump(credentials, pickle_file)

                # Set the position of the file-like object to the beginning
                pickle_file.seek(0)

                # Assign the file-like object to the `pickle_token` field
                instance.pickle_token.save('pickle_token.pkl', pickle_file)

                # Save the changes to the database
                instance.save()

        return Response({'idata': 'sdfds', 'pod': user}, status=status.HTTP_200_OK)

        # credentials = flow.fetch_token(
        #     authorization_response=request.build_absolute_uri(), code=authorization_code)
        # with open(temp_file.name, "wb") as token:
        #     instance = UserGmailToken.objects.get(user=userId)
        #     # data = {
        #     #     'pickle_token': pickle.dump(creds, token),
        #     #     'credentials': temp_file,
        #     #     'user': userId
        #     # }
        #     # Create a file-like object using io.BytesIO()
        #     pickle_file = io.BytesIO()

        #     # Dump the `creds` object into the file-like object
        #     pickle.dump(creds, pickle_file)

        #     # Set the position of the file-like object to the beginning
        #     pickle_file.seek(0)

        #     # Assign the file-like object to the `pickle_token` field
        #     instance.pickle_token.save('pickle_token.pkl', pickle_file)

        #     # Save the changes to the database
        #     instance.save()

        # # Save the credentials to the database
        # # Replace with your database save logic
        # save_credentials_to_db(credentials)

        # return HttpResponse("Credentials saved successfully.")


class TokenView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        tokenInstance = UserGmailToken.objects.filter(user=user)
        serializer = UserGmailTokenSerializer(tokenInstance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GmailOauthView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        FetchMail
        serializer = UserGmailTokenSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ExtraceSheet(APIView):

    def post(self, request):
        SHEET_ID = '1CNkSTtwgOPKNCPlLI1KPwzIOOz9GI6fW'
        SHEET_NAME = 'AAPL'
        url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx'
        df = pd.read_excel('users/output.xlsx')   
        index = df[df.eq('Electives for VIII Sem').any(axis=1)].index
        df.drop(range(index[0], len(df)), inplace=True)
        df.drop(1, inplace=True)
        new_heading = df.iloc[0].tolist()

        old_heading = df.columns.values.tolist()

        ziped_heading = zip(new_heading, old_heading)

        newDict = {}
        for newHead, oldHeading in list(ziped_heading):
            newDict[oldHeading] = newHead

        df.rename(columns=newDict, inplace=True)

        df.drop(0, inplace=True)

        df.reset_index(inplace=True)

        df.drop(['index'], axis=1, inplace=True)

        def replace_nan_value(df, column_name):
            skip_columns = ['Day', 'Batch Semester']
            prev_value = None
            column_name_value = df[column_name].tolist()
            newColumnValue = []
            for index, value in enumerate(column_name_value):
                if column_name not in skip_columns and index:
                    if df.at[index, 'Batch Semester'] != df.at[index - 1, 'Batch Semester']:
                        prev_value = None
                if not pd.isna(value): 
                    prev_value = value
                    
                newColumnValue.append(prev_value)
            df[column_name] = newColumnValue
            
        for head in df.columns.values.tolist():
            replace_nan_value(df, head)

        newRowArray = []
        prev_value = None

        for index, row in df.iterrows():
            for col_name, value in row.items():
                if not pd.isna(value):
                    prev_value = value
                newRowArray.append(prev_value)
                df.at[index, col_name] = prev_value

        mask = df.isnull()

        rows_with_nan = df[mask.any(axis=1)]
        columns_with_nan = df.columns[mask.any(axis=0)]


        df[columns_with_nan[0]]
        df.at[rows_with_nan.index[0], columns_with_nan[0]] = 'asdn'

        for column in columns_with_nan:
            for index in rows_with_nan.index:
                df.at[index, column] =  df[column][index+1]

        for head in df.columns.values.tolist():
            single_fields = ['Day', 'Batch Semester', 'Room', 'Group']
            if head not in single_fields:
                starting_time, ending_time = head.split(' ')
        #     Save to df with list 
            for value in df[head].tolist():
                if head == 'Day':
                    serializer = DaySerializer(data={'name': value})
                    if serializer.is_valid():
                        try:
                            serializer.save()                        
                        except Exception as e:
                            continue
                elif head == 'Batch Semester':
                    serializer = BatchSemesterSerializer(data={'name': value})
                    if serializer.is_valid():
                        try:
                            serializer.save()                        
                        except Exception as e:
                            continue
                elif head == 'Room':
                    serializer = RoomSerializer(data={'name': value})
                    if serializer.is_valid():
                        try:
                            serializer.save()                        
                        except Exception as e:
                            continue

                elif head == 'Group':
                    serializer = GroupSerializer(data={'name': value})
                    if serializer.is_valid():
                        try:
                            serializer.save()                        
                        except Exception as e:
                            continue
                else:
                    time_serializer = PeriodSeriallizer(data={'starting_time': '0', 'ending_time': "0", 'teacherName': {'name' : value}})
                    if time_serializer.is_valid():
                        try:
                            time_serializer.save()                        
                        except Exception as e:
                            continue
                    else: return Response({'data': time_serializer.errors}, status=status.HTTP_417_EXPECTATION_FAILED)
                    # serializer = TeacherWithSubjectSerializer(data={'name': value})
                    # if(time_serializer.is_valid()):
                    #     print('hiijij')
                    # if serializer.is_valid():
                    #     try:
                    #         serializer.save() 
                    #     except Exception as e:
                    #         continue
                
                        # return Response({'data': serializer.errors}, status=status.HTTP_417_EXPECTATION_FAILED)

                    


        df.to_excel('./new.xlsx')
        return Response({'data': df}, status=status.HTTP_200_OK)
