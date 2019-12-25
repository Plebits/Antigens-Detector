import glob
import RPi.GPIO as GPIO
import smtplib
import picamera, json, requests, os, random
from time import sleep
from PIL import Image, ImageDraw 

from gpiozero import Button
from signal import pause


# Importing modules for sending mail
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders


sender = 'sender_email'
password = 'sender_password'
receiver = 'receiver_email'



DIR = './home/pi/Desktop/Database/'
FILE_PREFIX = 'image'

            
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def send_mail(self):

    print 'Sending E-Mail'

    # Create the directory if not exists

    if not os.path.exists(DIR):

        os.makedirs(DIR)


    # Find the largest ID of existing images.

    # Start new images after this ID value.

    files = sorted(glob.glob(os.path.join(DIR, FILE_PREFIX + '[0-9][0-9][0-9].jpg')))

    count = 0

    

    if len(files) > 0:

        # Grab the count from the last filename.

        count = int(files[-1][-7:-4])+1

    # Save image to file

    filename = os.path.join(DIR, FILE_PREFIX + '%03d.jpg' % count)

    # Capture

    with picamera.PiCamera() as camera:

     pic = camera.capture(filename)

    print('caputred image')

    url = 'https://app.nanonets.com/api/v2/ImageCategorization/LabelFile/'

    data = {'file': open(filename, 'rb') , 'modelId': ('', '4c4cc949-122c-44f8-bed0-b6fa8b56a288')} 

    response = requests.post(url, auth= requests.auth.HTTPBasicAuth('-62qCGLTC_sgdy6RMkx6k644C68Ea1bF', ''), files=data) 


    print(response.text)

    #



    # Sending mail

    msg = MIMEMultipart()

    msg['From'] = sender

    msg['To'] = receiver

    msg['Subject'] = 'Plant Detected'

    

    body = 'Picture is Attached.'

    msg.attach(MIMEText(body, 'plain'))

    attachment = open(filename, 'rb')

    part = MIMEBase('application', 'octet-stream')

    part.set_payload((attachment).read())

    encoders.encode_base64(part)

    part.add_header('Content-Disposition', 'attachment; filename= %s' % filename)

    msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)

    server.starttls()

    server.login(sender, password)

    text = msg.as_string()

    server.sendmail(sender, receiver, text)

    server.quit()

GPIO.add_event_detect(15, GPIO.FALLING, callback = send_mail, bouncetime = 200)



pause()