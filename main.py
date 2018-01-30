"""
Execute the function
1. Analyze the daily emails in the mailbox. For each entry, extracts:
   - Invoice attached as PDF (Attachment must be a PDF, otherwise it's invalid)
   - Company which belongs to
2. Checks if exists a Google Drive folder for the matching company/year/month combination
  - If it doesn't exist, create it
3. Save the invoice in the the google drive folder and delete it from the mailbox
Run the function every day.
"""
import os
from base64 import b64decode
import boto3
from mailer import Mailer
from gmaker import GDocsMaker

def lambda_handler(event, context):
    email = decrypt_env(os.getenv('EMAIL_ADDRESS'))
    password = decrypt_env(os.getenv('PASS'))
    bucket_name = decrypt_env(os.getenv('BUCKET_NAME'))
    cred_bucket_name = decrypt_env(os.getenv('CRED_BUCKET_NAME'))
    cred_file_name = decrypt_env(os.getenv('CRED_FILE_NAME'))
    parent_folder_id = decrypt_env(os.getenv('PARENT_FOLDER_ID'))
    mailer = Mailer(email, password)
    emails = mailer.fetch_all()
    if len(emails) == 0:
        print("No emails available for processing")
        return 1

    for email in emails:
        path, company = mailer.download_attachment(email)
        if path is not None:
            print('Uploading invoice {} for company {}'.format(path, company))
            gmaker = GDocsMaker(company, cred_bucket_name, cred_file_name, parent_folder_id)
            gmaker.archive(path)
    print("Remove all the emails")
    mailer.remove_all()

def decrypt_env(env):
    """
    Decrypt the environment variables
    if we're in production
    """
    environment = os.getenv('ENVIRONMENT', 'PROD')
    if environment == 'STAGE':
        return env

    env_var = boto3.client('kms').decrypt(CiphertextBlob=b64decode(env))['Plaintext']
    return env_var.decode('utf-8')

if __name__ == '__main__':
    lambda_handler(None, None)
