from __future__ import print_function

import os

from documents.serializers import (DOCDocumentSerializer, ImageDocumentSerializer,
                               PDFDocumentSerializer, PPTDocumentSerializer, XLSXDocumentSerializer)
from datetime import datetime
from django.core.files import File

from .utils.gmail.create_filter import create_filter
from .utils.gmail.search_message import search_messages
from .utils.gmail.read_message import read_message
from .utils.gmail.get_authenticate import get_authenticate
from .utils.detector import is_pdf, is_ppt, is_docx, is_xlsx, is_image


class FetchMail:
    def __init__(self, user, credintials):
        self.user = user
        self.creds = None
        self.credintials = credintials
        self.service = get_authenticate(self.credintials)

    def display_message(self, message_id):
        """This will save the mail in the Mails folder and display on command line"""
        return read_message(self.service, message_id)

    def search_message(self, query):
        """This will return the message Id and you have to read the message with function display_message"""
        filter_id = create_filter(self.service)
        return search_messages(self.service, query, filter_id=filter_id)

    def run(self):
        messages = self.search_message('Nepal Engineering College')
        print('user', self.user)

        for msg in messages[:5]:
            print(self.display_message(msg))


class CheckMail:
    def __init__(self, user, root_dir=os.getcwd()):
        self.user = user
        self.root_dir = root_dir

    def save_db(self, Serializer, file_path):
        """This will save the file in the database"""
        print(self.user)
        data = {
            'file': File(open(file_path, 'rb'), name=os.path.basename(file_path)),
            'user': self.user['id'],
            'semester': self.user['semester_id'],
            'faculty': self.user['faculty_id'],
        }
        serializer = Serializer(data=data)
        if serializer.is_valid():
            serializer.save()
        else:
            print(serializer.errors)

    def check_pdf(self, file_path, file):
        """This will check if the file is pdf or not and save in a file with path name. If not then it will remove it."""

        if is_pdf(file_path):
            self.save_db(PDFDocumentSerializer, file_path)
        elif is_docx(file_path):
            self.save_db(DOCDocumentSerializer, file_path)
        elif is_ppt(file_path):
            self.save_db(PPTDocumentSerializer, file_path)
        elif is_xlsx(file_path):
            self.save_db(XLSXDocumentSerializer, file_path)
        elif is_image(file_path):
            self.save_db(ImageDocumentSerializer, file_path)
        else:
            try:
                os.remove(file_path)
                print(f'{file} is not a PDF. So Removed it.')
            except OSError as e:
                print(f"Error: {e.file} - {e.strerror}.")

    def remove_empty_dir(self, dir):
        """This will check if the directory is empty or not. If empty then it will remove it."""
        try:
            if (os.listdir(dir) == []):
                os.rmdir(dir)
        except Exception as e:
            print(f"Error: {e}.")

    def navigate_folder(self, dir):
        """This will navigate through the folder and check if the file is pdf or not. If not then it will convert it to pdf. Else it will remove it."""
        for folders in os.listdir(dir):
            folder_path = os.path.join(dir, folders)
            print('\n')
            try:
                for file in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, file)
                    print(f'Checking file: {file_path}')
                    # self.convert_to_pdf(file_path, folder_path)
                    self.check_pdf(file_path, file)

            except NotADirectoryError as e:
                print(f"Error: {e}.")
            self.remove_empty_dir(folder_path)

    def run(self, dir='Mails'):
        print(os.listdir(dir))
        self.navigate_folder(dir)
