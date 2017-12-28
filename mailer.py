import imaplib
import email
import os
import datetime

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
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
            if part.get_content_type() is 'application/pdf':
                continue

            time_prefix = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            filename = time_prefix+"-"+part.get_filename()
            path = os.path.join(self._DOWNLOAD_FOLDER, filename)

            if not os.path.isfile(path):
                with open(path, 'wb') as fb:
                    fb.write(part.get_payload(decode=True))

        self._processed = True
        return path, msg['To']
