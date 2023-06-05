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
        credientials  = UserGmailToken.objects.filter(user=email)
        serializerCreds = UserGmailTokenSerializer(credientials, many=True)


        # Run the email fetching operation in a separate thread
        thread = threading.Thread(target=self.fetch_mail, args=(user, serializerCreds.data,))
        thread.start()

        thread.join()

        thread = threading.Thread(target=self.save_file, args=(user,))
        thread.start()

        thread.join()

        return Response("Email fetching started.", status=200)

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import requests
import tempfile
import io
import pickle


class OauthLink(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]


    def post(self, request):
        email = request.user
        user = CustomUser.objects.filter(email=email).values().first()
        print('user', user)
        instance  = UserGmailToken.objects.filter(user=email)
        print('instance', instance)
        credentials = UserGmailTokenSerializer(instance, many=True)
        file_content = get_data_from_url(f'http://localhost:8000{list(credentials.data)[0]["credentials"]}')
        # pickle_content = get_data_from_url(f'http://localhost:8000{list(credentials.data)[0]["pickle_token"]}')
        authorization_url=None
        scheme = request.scheme
        host = request.get_host()
        base_url = f"{scheme}://{host}"
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file_content.content)
            temp_file.flush()
            flow = InstalledAppFlow.from_client_secrets_file(temp_file.name, SCOPES, redirect_uri=f'{base_url}/users/oauth2callback/?user={email}')
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

        instance  = UserGmailToken.objects.filter(user=user['id'])
        credentials = UserGmailTokenSerializer(instance, many=True)
        scheme = request.scheme
        host = request.get_host()
        base_url = f"{scheme}://{host}"

        file_content = get_data_from_url(f'{base_url}{list(credentials.data)[0]["credentials"]}')
        # pickle_content = get_data_from_url(f'http://localhost:8000{list(credentials.data)[0]["pickle_token"]}')
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file_content.content)
            temp_file.flush()
            flow = InstalledAppFlow.from_client_secrets_file(temp_file.name, SCOPES, redirect_uri=f'{base_url}/users/oauth2callback/?user={email}')
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

        credentials = flow.fetch_token(authorization_response=request.build_absolute_uri(), code=authorization_code)
        with open(temp_file.name, "wb") as token:
            instance = UserGmailToken.objects.get(user=userId)
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
        
        # Save the credentials to the database
        save_credentials_to_db(credentials)  # Replace with your database save logic

        return HttpResponse("Credentials saved successfully.")


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