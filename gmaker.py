"""
This class establishes a connection with the Google API,
create a dir structure and create the file on it.
"""

import os
import mimetypes
import re
import boto3
from google.oauth2 import service_account
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload
import datetime


class GDocsMaker():

    def __init__(self, company_name, cred_bucket_name, cred_file_name, parent_folder_id):
        """
        @var company_name: the name of the company
        @var cred_bucket_name: the name of the bucket where the GAPI credential file is stored
        @var cred_file_name: the name of the GAPI credential file
        @var parent_folder_id: the parent folder id where the dir structure will be created.
        """
        self.__folder_struct = self.__get_folder_struct(company_name)
        self.__cred_file_name = cred_file_name
        self.__parent_folder_id = parent_folder_id
        self.__download_credential_file(cred_bucket_name)

    def __get_folder_struct(self, company_name):
        """
        Retrive all the elements which compose the
        dir structure
        """

        return [
            company_name.lower().title(),
            str(datetime.datetime.now().year),
            datetime.datetime.now().strftime("%B")
        ]

    def __get_service(self):
        """
        Establish a connection with the Google API
        and authorize the access to the Google Drive APIs
        """

        scopes = [
            'https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/drive.metadata.readonly']
        service_account_file = '/tmp/'+self.__cred_file_name
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file, scopes=scopes
        )
        return googleapiclient.discovery.build('drive', 'v3', credentials=credentials, cache_discovery=False)
    
    def __download_credential_file(self, cred_bucket_name):
        """
        Download the Google API Credential file from the
        remote S3 bucket and stored in a local folder
        """

        client = boto3.client('s3')
        with open('/tmp/'+self.__cred_file_name, 'wb') as file:
            client.download_fileobj(cred_bucket_name, self.__cred_file_name, file)
    
    def __create_folder(self, folder, folder_id):
        """
        Create the directory structure
        """

        parent = self.__get_service().files().list(q="name='{}' and '{}' in parents".format(folder, folder_id), fields='files(id, name)').execute()
        if not parent['files']:
            file_metadata = {
                'name': folder,
                'mimeType':'application/vnd.google-apps.folder',
                'parents':[folder_id]
            }
            file = self.__get_service().files().create(body=file_metadata,fields='id').execute()
            return file.get('id')
        else:
            return parent['files'][0]['id']

    def __upload(self, file, parent_id):
        """
        Upload the file in the directory structured created
        on the Google Drive
        """

        mimetypes.init()
        mime_type = mimetypes.guess_type(file)
        filename = re.sub(r'\/tmp\/', '', file)
        if mime_type[0] is not None:
            file_metadata = {
                'name':filename,
                'parents':[parent_id]
            }
            media = MediaFileUpload(file, mimetype=mime_type[0])
            uploaded_file = self.__get_service().files().create(body=file_metadata, media_body=media, fields='id').execute()
            return uploaded_file.get('id')
    
    def archive(self, file):
        """
        Put all together
        """

        folder_id = self.__parent_folder_id
        for folder in self.__folder_struct:
            folder_id = self.__create_folder(folder, folder_id)
        
        self.__upload(file, folder_id)
        