import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from constants import ADMIN_EMAIL
from run_timer import cmd_output_end, cmd_output_start


def make_email_message(signals_sum):
    start_time = cmd_output_start('Detecting...')

    trendirany = []
    korrekcio = []
    for signals in signals_sum:
        for signal in signals:
            if signal.orientation == signal.trend and signal.orientation == signal.sector_trend:
                trendirany.append(signal)
            else:
                korrekcio.append(signal)

    with open('previous_mail.txt', "r") as file:
        previous_mail = file.read()

    new_signal = False
    str_trendirany = "Trendiranyu dimbesdombos\n\n"
    str_not_changed_signals = str_trendirany
    for signal in trendirany:
        signal_str = signal.instrument + " - " + signal.timeframe.name + ": " \
                     + signal.orientation.name + "\t\t|\t\t" + str(signal.peak_timestamp) + " - " + str(signal.value) \
                     + "\n"
        if signal_str in previous_mail:
            str_not_changed_signals = str_not_changed_signals + signal_str
        else:
            str_not_changed_signals = str_not_changed_signals + signal_str
            str_trendirany = str_trendirany + signal_str
            new_signal = True

    print("\nMail content:\n\n" + str_trendirany)

    with open('previous_mail.txt', "w") as file:
        file.write(str_not_changed_signals)

    file.close()

    cmd_output_end(start_time)

    str_korrekcio = "Korrekcios dimbesdombos\n\n"
    for signal in korrekcio:
        str_korrekcio = str_korrekcio + signal.instrument + " - " + signal.timeframe.name + ": " \
                        + signal.orientation.name + " " + str(signal.peak_timestamp) + " " + str(signal.value) \
                        + "\n"
    print(str_korrekcio)
    return str_trendirany, new_signal


def send_email(user, debug, mail_content):
    start_time = cmd_output_start('Sending email...')

    if debug:
        yes = input('Send email?(y): ')
    else:
        yes = 'y'
    if yes == 'y':

        # The mail addresses and password
        sender_address = 'db.mt.obd@gmail.com'
        sender_pass = 'xQiG158CD40uV7TXLeIC'
        receiver_address = [ADMIN_EMAIL]

        # Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_address
        if user:
            file = open('user_emails.txt', "r")
            emails = file.read().split("\n")
            file.close()
            receiver_address += emails

        print(receiver_address)
        message['To'] = ','.join(receiver_address)
        message['Subject'] = "MT dimbes-dombos"

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