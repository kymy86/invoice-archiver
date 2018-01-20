import imaplib
import email
import os
import datetime
import boto3
import base64

class Mailer():

    _mailconn = None
    _DOWNLOAD_FOLDER = '/tmp'
    _processed = False

    def __init__(self, email, pwd, smtp_server='imap.gmail.com', smtp_port=993):
        """
        Estabilished a connection with the mailbox
        """
        self._email = email
        self._pwd = pwd

        self._mailconn = imaplib.IMAP4_SSL(smtp_server, smtp_port)
        self._mailconn.login(self._email, self._pwd)
        self._mailconn.select(readonly=False)
        self._client = boto3.client('dynamodb')

    def close_mail_connection(self):
        """
        Close the connection with the mailbox
        """
        self._mailconn.close()

    def fetch_all(self):
        """
        Retrieve all the email from the mailbox
        """
        emails = []
        res, messages = self._mailconn.search(None, 'ALL')
        if res == 'OK':
            for msg in messages[0].split():
                try:
                    res, data = self._mailconn.fetch(msg.decode('utf-8'), '(RFC822)')
                except Exception as error:
                    self.close_mail_connection()
                    print('No email to read: '+error)
                    exit()
                
                msg = email.message_from_string((data[0][1]).decode('utf-8'))
                if not isinstance(msg, str):
                    if self.is_sender_in_whitelist(msg['From']):
                        emails.append(msg)

        return emails

    def remove_all(self):
        """
        If the emails are processed correctly
        removed them from the mailbox
        """
        if self._processed:
            res, messages = self._mailconn.search(None, 'ALL')
            if res == 'OK':
                for msg in messages[0].split():
                    res, data = self._mailconn.store(msg.decode('utf-8'), '+FLAGS', '\\Deleted')
                    print(res)

    def download_attachment(self, msg):
        """
        Download the attachment from the email
        and return the path and the destination email address
        """
        path = None
        for part in msg.walk():
            if part.get_content_type() == 'application/pdf':

                time_prefix = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                filename = time_prefix+"-"+part.get_filename()
                path = os.path.join(self._DOWNLOAD_FOLDER, filename)

                if not os.path.isfile(path):
                    with open(path, 'wb') as fb:
                        fb.write(part.get_payload(decode=True))

        self._processed = True
        return path, self.get_company(msg['From'], msg['To'])

    def _extract_email_address(self, from_email):
        """
        Extract the email address from the "FROM" field
        """
        res = email.utils.parseaddr(from_email)
        if len(res[1]) != 0:
            return res[1].lower()
        else:
            print(res, from_email)
            return ""

    
    def is_sender_in_whitelist(self, from_email):
        """
        Check if the email address is in the whitelist or not
        """
        
        res = self._client.get_item(
            TableName='WhitelistSender',
            Key={
                'sender':{
                    'S':self._extract_email_address(from_email)
                }
            }
        )
        if 'Item' in res:
            return True
        else:
            return False
    
    def get_company(self, from_email, to_email):
        """
        Return the company name based on
        the email address by doing a lookup on the DynamoDB
        Table
        """
        to_email = self._extract_email_address(to_email)
        from_email = self._extract_email_address(from_email)
        # use from and to email addresses combination as a primary key
        _id = base64.b64encode(bytes(from_email+"-"+to_email, encoding='utf-8'))
        res = self._client.get_item(
            TableName='Company',
            Key={
                'id':{
                    'S':_id.decode('utf-8')
                }
            }
        )
        if 'Item' in res:
            return res['Item']['company']['S']
        else:
            return 'unknown'

