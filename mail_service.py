# Copyright (c) 2021 Cisco and/or its affiliates.

# This software is licensed to you under the terms of the Cisco Sample
# Code License, Version 1.1 (the "License"). You may obtain a copy of the
# License at

#                https://developer.cisco.com/docs/licenses

# All use of the material herein must be in accordance with the terms of
# the License. All rights not expressly granted by the License are
# reserved. Unless required by applicable law or agreed to separately in
# writing, software distributed under the License is distributed on an "AS
# IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied.

import os
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

# load all environment variables
load_dotenv()

SENDER_EMAIL = os.environ['SENDER_EMAIL']
SENDER_PW = os.environ['SENDER_PW']

APP_URL = os.environ['APP_URL']


def createSponsorEmailContents(username, firstname, lastname):
    title = "Guest Approval Request"
    htmlContent = """\
            <html>
            <head></head>
            <body>
                <p>
                Please approve (or deny) this self-registering guest. The guest provided the following information: <br/>
                Username: """+username+"""<br/>
                First Name: """+firstname+""" <br/>
                Last Name: """+lastname+"""<br/>
                <a href='"""+APP_URL+"""/approve?username="""+username+"""'>Approve</a><br/>
                <a href='"""+APP_URL+"""/deny?username="""+username+"""'>Deny</a>
                </p>
            </body>
            </html>
            """
    textContent = """Please approve (or deny this self-registering guest. The guest provided the following information: Username: """+username+""", First Name """+firstname+""", Last Name """+lastname+""".
                <a href='"""+APP_URL+"""/approve?username="""+username+"""'>Approve</a><br/>
                <a href='"""+APP_URL+"""/deny?username="""+username+"""'>Deny</a>"""

    return title, htmlContent, textContent

def createGuestSuccEmailContents():
    title = "Guest Account Approved"
    htmlContent = """\
                    <html>
                    <head></head>
                    <body>
                        <p>
                        Your guest account approval request has been approved for 6 months.<br/>
                        </p>
                    </body>
                    </html>
                    """
    textContent = """Your guest account approval request has been approved for 6 months."""
    return title, htmlContent, textContent

def createGuestDenyEmailContents():
    title = "Guest Account Denied"
    htmlContent = """\
                    <html>
                    <head></head>
                    <body>
                        <p>
                        Your guest account approval request has been denied. Your access has been suspended.<br/>
                        </p>
                    </body>
                    </html>
                    """
    textContent = """Your guest account approval request has been denied. Your access has been suspended."""
    
    return title, htmlContent, textContent

   
def sendMail(user, type, sponsorMail):

    if type == 'guestSucc':
        title, html, text = createGuestSuccEmailContents()
        receiver = user['guestInfo']['emailAddress']
    elif type == 'guestDeny':
        title, html, text = createGuestDenyEmailContents()
        receiver = user['guestInfo']['emailAddress']
    elif type == 'sponsor':
        receiver = sponsorMail
        title, html, text = createSponsorEmailContents(user['name'], user['guestInfo']['firstName'], user['guestInfo']['lastName'])

    sender = SENDER_EMAIL
    
    # Create message container 
    msg = MIMEMultipart('alternative')
    msg['Subject'] = title
    msg['From'] = sender
    msg['To'] = receiver

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    # Send the message via local SMTP server.
    mail = smtplib.SMTP('smtp.gmail.com', 587)

    mail.ehlo()

    mail.starttls()

    mail.login(SENDER_EMAIL, SENDER_PW)
    mail.sendmail(sender, receiver, msg.as_string())
    mail.quit()