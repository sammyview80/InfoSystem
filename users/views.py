from google.oauth2 import service_account
from urllib.parse import urlparse, parse_qs
import gspread
import json
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
from utils.extractSheet import ExtractSheet
from routine.models import Day, BatchSemester, Room, Group, TeacherWithSubject, Period, AutoMatedRoutine
from routine.serializers import DaySerializer, BatchSemesterSerializer, RoomSerializer, GroupSerializer, PeriodSeriallizer, TeacherWithSubjectSerializer, AutoMatedRoutineSerializers
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from utils.CustomeResponse import CustomeResponse
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly",
          "https://www.googleapis.com/auth/gmail.modify"]


class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return CustomeResponse({'data': serializer.data, 'message': 'Login Sucessfully.'}, status=status.HTTP_201_CREATED)
        return CustomeResponse({'data': serializer.errors, 'message': 'Cannot register user'}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class UserLoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if email is None or password is None:
            return Response("Email and password are required fields.", status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return CustomeResponse({'message': "User successfully logged in.", 'data': {'email': user.get_username()}}, status=status.HTTP_200_OK)
        else:
            return CustomeResponse({'message': "Invalid email or password.", 'data': f'{email} is unknown'}, status=status.HTTP_401_UNAUTHORIZED)


class UserDetailView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return CustomeResponse({'data': serializer.data, 'message': 'Sucessfully get user.'}, status=status.HTTP_200_OK)


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

        return CustomeResponse({'data': user, 'message': 'User successfully updated'})


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


class ExtraceSheetView(APIView):

    def post(self, request):
        SHEET_ID = '1CNkSTtwgOPKNCPlLI1KPwzIOOz9GI6fW'
        SHEET_NAME = 'AAPL'
        url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx'

        sheet = ExtractSheet('users/output.xlsx')
        sheet.remove_unwanted_columns(
            ['Electives for VIII Sem'], sheet.__len__)
        sheet.rename_heading(0)
        sheet.remove_unwanted_columns_index(0)
        sheet.replace_nan_value_column_all()
        sheet.replace_nan_value_row_all()
        df = sheet.replace_nan_value_all()

        print(df)
        # return CustomeResponse({'data': df.to_json(), "message": 'Json data retrive sucess.'}, status=status.HTTP_200_OK)

        for head in df.columns.values.tolist():
            single_fields = ['Day', 'Batch Semester', 'Room', 'Group']
            if head not in single_fields:
                starting_time, ending_time = head.split(' ')
        #     Save to df with list
            for index, value in enumerate(df[head]):
                # value = value.replace(" ", "").lower()
                if head == 'Day':
                    serializer = DaySerializer(data={'name': value})
                    prev_day = value
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
                    # time_serializer = PeriodSeriallizer(
                    #     data={'starting_time': '0', 'ending_time': "0", 'teacherName': {'name': value}})
                    # if time_serializer.is_valid():
                    #     try:
                    #         time_serializer.save()
                    #     except Exception as e:
                    #         continue
                    # else:
                    #     return Response({'data': time_serializer.errors}, status=status.HTTP_417_EXPECTATION_FAILED)
                    serializer = TeacherWithSubjectSerializer(
                        data={'name': value})

                    if serializer.is_valid():
                        try:
                            serializer.save()
                        except Exception as e:
                            continue
                    try:

                        TeacherSub = TeacherWithSubject.objects.get(
                            name=value)
                        row = df.loc[index, 'Day']
                        print(row)
                        day = Day.objects.get(name=row)
                    except TeacherWithSubject.DoesNotExist:
                        pass
                    if row == 'Wednesday':
                        print(row, starting_time, ending_time,
                              TeacherSub.id, day.id)
                    period_serializer = PeriodSeriallizer(
                        data={"starting_time": starting_time, "ending_time": ending_time, 'teacherName': TeacherSub.id, 'day': day.id})
                    if (period_serializer.is_valid(raise_exception=True)):
                        period_serializer.save()
                    else:
                        return Response({'data': serializer.errors}, status=status.HTTP_417_EXPECTATION_FAILED)

        # Save in to db fom row iteration
        for index, row in df.iterrows():
            periods_value = []
            sub_all_value = []
            for col_name, value in row.items():

                single_fields = ['Day', 'Batch Semester', 'Room', 'Group']

                # break
                # value = value.replace(" ", "").lower()

                if col_name == 'Day':
                    day = Day.objects.get(
                        name=value)
                    sub_all_value.append(day.id)
                    day_value = day
                elif col_name == 'Batch Semester':
                    try:

                        batchSem = BatchSemester.objects.get(name=value)
                    except BatchSemester.DoesNotExist:
                        pass
                    sub_all_value.append(batchSem.id)
                elif col_name == 'Room':
                    room = Room.objects.get(name=value)
                    sub_all_value.append(room.id)

                elif col_name == 'Group':
                    group = Group.objects.get(name=value)
                    sub_all_value.append(group.id)
                periods = []
                if col_name not in single_fields:
                    starting_time, ending_time = col_name.split(' ')
                    try:

                        TeacherSub = TeacherWithSubject.objects.get(
                            name=value)
                    except TeacherWithSubject.DoesNotExist:
                        pass
                    period = Period.objects.filter(
                        teacherName=TeacherSub.id, starting_time=starting_time, ending_time=ending_time, day=day_value.id).values('id').distinct()
                    # print(period)
                    # for item in period:
                    #     a = Period.objects.filter(
                    #         teacherName_id=item['teacherName'])
                    if len(period) > 0:
                        sub_all_value.append(list(period))

                    # sub_all_value.append(list(period))
            if 5 < len(sub_all_value):
                if len(sub_all_value[4]) > 0:
                    serializer = AutoMatedRoutineSerializers(data={
                        'day': sub_all_value[0],
                        'batchSemester': sub_all_value[1],
                        'room': sub_all_value[2],
                        'group': sub_all_value[3],
                        'period': [period['id'] for period in sub_all_value[4]]
                    })
                    serializer.is_valid(raise_exception=True)
                    serializer.save()

        # print(all_value)
        df.to_excel('./new.xlsx')
        return Response({'data': df}, status=status.HTTP_200_OK)


class GetDataFromUrl(APIView):
    def get(self, request):
        sheet_url = request.query_params.get(
            'sheet_url') or 'https://docs.google.com/spreadsheets/d/1NRd3pMD9S2sEnt1mhqBAj_07z-dwRGbFANMsD4ReFL0/edit#gid=934131427'
        scopes = ['https://www.googleapis.com/auth/spreadsheets',
                  'https://www.googleapis.com/auth/drive']
        credentials = service_account.Credentials.from_service_account_file(
            'mail/drive-creds.json', scopes=scopes)
        client = gspread.authorize(credentials)

        # sheet_url = 'https://docs.google.com/spreadsheets/d/1NRd3pMD9S2sEnt1mhqBAj_07z-dwRGbFANMsD4ReFL0/edit#gid=934131427'
        sheet_name = 'classes'

        sheet = client.open_by_url(sheet_url).worksheet(sheet_name)

        print('sheet', sheet)
        data = sheet.get_all_values()

        data = pd.read_json(json.dumps(data))
        data.to_excel('./fetched.xlsx')
        print(data)

        return Response({'data': data}, status=status.HTTP_200_OK)
