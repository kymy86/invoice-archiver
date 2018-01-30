# Invoice Archiver ![version][version-badge]

[version-badge]: https://img.shields.io/badge/version-2.0.0-blue.svg

This [Amazon Lambda] function reads all the emails in a given mailbox, it downloads all the attachments and move them in a Google Drive folder. The function relies on a couple of DynamoDB table to work. In particular:

- **WhitelistSender**: Only the email sent from this email addresses are allowed to be processed.
- **Company**: By combining the sender and receiver email addresses, we compute the company which the emails belong to. This is used as the parent folder name where the attachments are saved.

To save the files in the Google Drive folder, the Google Python SDK is used. The authentication flow has been implementing by following the [OAuth 2.0 Server to Server Application] flow.
The Lambda function is deployed by using the [Zappa] Framework.
The default trigger for the function is a CloudWatch scheduled Event.

[Amazon Lambda]: https://aws.amazon.com/lambda/
[Zappa]: https://www.zappa.io/
[OAuth 2.0 Server to Server Application]: https://developers.google.com/api-client-library/python/auth/service-accounts

## Getting Started

1. Run the **archiver.yml** CloudFormation template to create the S3 Bucket, two DynamoDB tables and the Lambda Function Role.
2. Install the Zappa framework `pip install --upgrade zappa`
3. Optional: configure the Zappa framework from the **zappa_settings.yml** file
4. Pass the AWS region you chose to the BucketMaker constructor
5. Deploy the Lambda function with the command `zappa deploy`
6. In the AWS Lambda console, set-up the following Environment variables:
    - EMAIL_ADDRESS: the mailbox where reads the emails
    - PASS: the mailbox password
    - BUCKET_NAME: the name of the bucket where the attachments will be saved
    - CRED_BUCKET_NAME: the name of the bucket where the Google Api credential file is saved
    - CRED_FILE_NAME: the name of the Google Api credential file
    - PARENT_FOLDER_ID: the Google Drive the parent folder ID where the directory structure will be created and the the attachment will be saved.

## Directory Structure

All the attachments will be saved in the following directory structure:

```
|Parent folder (identified by the ID passed as PARENT_FOLDER_ID)
|
|-- Company Name
    |
    |--- Current Year
        |
        |--- Current Month
```

**N.B.** If you want to test the function on your local machine, set-up a *ENVIRONMENT* environment variable to STAGE, so that the the KMS encryption is not applied.