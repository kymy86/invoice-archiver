"""
N.B. This class is related to the first version of this lambda function,
where the attachments were saved on a S3 bucket. 
In the current version, this is not used anymore.
"""

import os
import mimetypes
import re
import boto3
from botocore import exceptions
import datetime

class BucketMaker():

    def __init__(self, company_name, bucket_name, bucket_region):
        self.__folder_name = self.__get_folder_name(company_name)
        self.__client = boto3.client('s3')
        self.__bucket_name = bucket_name
        self.__bucket_region = bucket_region
    

    def __get_folder_name(self, company_name):
        """
        Return the folder name
        """
        return company_name.lower().title()+"/"+str(datetime.datetime.now().year)+"/"+datetime.datetime.now().strftime("%B")+"/"

    def __bucket_exists(self):
        """
        Check if bucket exists
        """
        try:
            self.__client.head_bucket(Bucket=self.__bucket_name)
            return True
        except exceptions.ClientError:
            return False

    def __create_bucket(self):
        """
        Create the bucket
        """
        self.__client.create_bucket(
            Bucket=self.__bucket_name,
            CreateBucketConfiguration={
                'LocationConstraint':self.__bucket_region
            }
        )

    def __upload(self, file):
        """
        Upload file in the bucket
        """
        mimetypes.init()
        mime_type = mimetypes.guess_type(file)
        filename = re.sub(r'\/tmp\/', '', file)
        if mime_type[0] is not None:
            self.__client.upload_file(file,
                                      self.__bucket_name,
                                      self.__folder_name+filename,
                                      ExtraArgs={'ContentType':mime_type[0]})

    def archive(self, file):
        """
        Creates the bucket if it doesn't exist
        and uplads the file.
        """
        if not self.__bucket_exists():
            self.__create_bucket()
        self.__upload(file)
