import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from constants import ADMIN_EMAIL
from run_timer import cmd_output_end, cmd_output_start


def send_email(mail_content, subject, user=False, debug=True):
    start_time = cmd_output_start('Sending email...')

    if debug:
        yes = input('Send email?(y): ')
    else:
        yes = 'y'
    if yes == 'y':

        file = open('../sender_cred.txt', "r")
        credentials = file.read().split("\n")
        file.close()
        if len(credentials) > 2: print('Broken sender_cred.txt: too much line')

        # The mail addresses and password
        sender_address = credentials[0]
        sender_pass = credentials[1]
        receiver_address = [ADMIN_EMAIL]

        # Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_address

        if user:
            file = open('../user_emails.txt', "r")
            emails = file.read().split("\n")
            file.close()
            receiver_address += emails

        print(receiver_address)
        message['To'] = ','.join(receiver_address)
        message['Subject'] = subject

        # The body and the attachments for the mail
        message.attach(MIMEText(mail_content, 'plain'))

        # Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
        session.starttls()  # enable security
        session.login(sender_address, sender_pass)  # login with mail_id and password
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()
        print('Mail Sent')

    cmd_output_end(start_time)
