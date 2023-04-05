import smtplib
from cms.conf import config


def sendMailNoAuth(receiver, subject, msg):
    """
    Static method to send mail with the given parameters
    @param receiver: The mail address to which we wanna send the mail
    @param subject: The Subject of the mail
    @param msg: The msg of the mail
    @return: True if successful, False if Error occurs.
    """
    try:
        with smtplib.SMTP(host=config.smtpHost, port=config.smtpPort) as server:
            message_text = ("From: " + config.smtpSender + "\n" + "To: " + receiver + "\n" + "Subject: " + subject + "\n\n" + msg)
            server.sendmail(sender, config.smtpSender, message_text)

            text = ("From: " + sender + " To: " + receiver + " Subject: " + subject)
        return True

    except Exception as err:
        return False
