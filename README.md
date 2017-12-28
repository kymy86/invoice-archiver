# Invoice Archiver

This [Amazon Lambda] function reads all the emails in a given mailbox, it downloads all the attachments and move them in a S3 bucket.

The Lambda function is deployed by using the [Zappa] Framework.
The default trigger for the function is a CloudWatch scheduled Event.

[Amazon Lambda]: https://aws.amazon.com/lambda/
[Zappa]: https://www.zappa.io/

## Getting Started

1. Run the **archiver.yml** CloudFormation template to create the S3 Bucket and the Lambda Function Role.
2. Install the Zappa framework `pip install --upgrade zappa`
3. Optional: configure the Zappa framework from the **zappa_settings.yml** file
4. Pass the bucket name and the AWS region you chose to the BucketMaker constructor
5. Deploy the Lambda function with the command `zappa deploy`
6. In the AWS Lambda console, set-up the following Environment variables:
    - EMAIL_ADDRESS: the mailbox where reads the emails
    - PASS: the mailbox password

**N.B.** If you want to test the function on your local machine, set-up a *ENVIRONMENT* environment variable to STAGE, so that the the KMS encryption is not applied.