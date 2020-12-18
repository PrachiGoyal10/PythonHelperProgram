import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import configparser
import os
import logging
from datetime import datetime



def setup_logger(path,name):
    logger = logging.getLogger(name)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s',datefmt='%a, %d-%b-%Y %H:%M:%S -')
    path = os.path.join(os.path.dirname(__file__), path)
    directory = os.path.dirname(path)
    if not os.path.exists(path):
        os.makedirs(path)
    fileHandler = logging.FileHandler( path + name + datetime.now().strftime('log_%Y_%m_%d_%h.log'), mode='a')
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)
    logger.setLevel(level=logging.INFO)
    if (logger.hasHandlers()):
        logger.handlers.clear()
    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)
    return logger


def send_mail(emaillog, mailBody):
    try:
        config =configparser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), "in.cfg"))
        SMTP_Server = config['EmailDetails']['SMTPServerIP']
        SMTPUserNM = config['EmailDetails']['SMTPUserNM']
        SMTPpassword = config['EmailDetails']['SMTPpassword']
        SMTPPort = config['EmailDetails']['portNo']

        SMTPServiceEmailID = config['EmailDetails']['SMTPServiceEmailID']
        toAddr = config['EmailDetails']['toAddr']
        subject = config['EmailDetails']['subject']

        msg = MIMEMultipart()
        msg['From'] = SMTPServiceEmailID
        msg['To'] = toAddr
        msg['Subject'] = subject
        body = MIMEText(mailBody)
        msg.attach(body)




        with smtplib.SMTP(SMTP_Server, SMTPPort, timeout=120) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            if SMTPUserNM and SMTPpassword:
                server.login(SMTPUserNM, SMTPpassword)
            server.sendmail(SMTPServiceEmailID, toAddr, msg.as_string())
           # server.quit()

    except smtplib.SMTPAuthenticationError:
        emaillog.error( "The username and/or password you entered is incorrect")
        raise
    except smtplib.SMTPServerDisconnected:
        emaillog.error('Failed to connect to the server. Wrong user/password?')
        raise
    except smtplib.SMTPException as e:
        emaillog.error('SMTP error occurred: ' + str(e))
        raise
    except Exception as e:
        emaillog.error("-Some Exception occured while sending email. "+str(e))
        if "STOREDRV.ClientSubmit; sender thread limit exceeded" in str(e):
            emaillog.info("-Trying to mail again as it failed because of thread limit.")
            send_mail(emaillog,mailBody)
        if "Connection unexpectedly closed: timed out" in str(e):
            emaillog.info(" Trying to mail again as it failed because - Connection unexpectedly closed: timed out.")
            send_mail(emaillog,mailBody)



if __name__ == '__main__':
    name = "Email_Alerting"
    path = 'Logs/'
    logs = setup_logger(path,name)
    try:
        logs.info("SCRIPT STARTED")
        mailBody = "Hi this is a test e-mail...."
        send_mail(logs, mailBody)
    except Exception as e:
        logs.error("Script ended with exception...."+str(e))
    finally:
        logs.info("Script completed")