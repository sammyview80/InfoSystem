from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, UserGmailTokenSerializer
# from fileManager.mail.main import FetchMail, CheckMail
from mail.main import FetchMail, CheckMail
from django.contrib.auth import authenticate, login
import asyncio
import threading
from .models import CustomUser, UserGmailToken
from django.shortcuts import get_object_or_404


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


class TokenView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        tokenInstance = UserGmailToken.objects.filter(user=user)
        serializer = UserGmailTokenSerializer(tokenInstance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
