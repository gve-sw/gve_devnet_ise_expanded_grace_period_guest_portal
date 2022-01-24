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

from flask import Flask, render_template, request
import json
import os
import urllib3

import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

import mail_service
import api_service

urllib3.disable_warnings()

app = Flask(__name__)

'''Intervall in which script checks for new users for whom the approval process has not yet been started'''
SCHEDULER_INTERVAL_SEC = int(os.environ['SCHEDULER_INTERVAL_SEC'])

'''
Triggered when approve link in email is clicked by sponsor.
'''
app.route('/approve?username=<username>')
@app.route('/approve', methods=["POST", "GET"])
def approve():
    
    print('--------APROVING TRIGGERED VIA EMAIL----------')
    username = request.args.get('username')
    user = json.loads(api_service.getGuestUserbasedOnName(username))
    
    if 'GuestUser' in user and 'ui_approve_text_label' in user['GuestUser']['customFields'] and user['GuestUser']['customFields']['ui_approve_text_label'] == 'waiting':
        
        #update guestuser to have access for 180 days and change approval state to 'approved' 
        updateInfo = api_service.updateGuestUserByName(user['GuestUser']['name'], 180, 'approved')
        print(updateInfo)
        
        #inform guest user about approved request
        mail_service.sendMail(user['GuestUser'], 'guestSucc', '') 
        
        return render_template("approved.html", username=username)
    
    return render_template("invalidRequest.html", username=username)


'''
Triggered when deny link in email is clicked by sponsor.
'''
app.route('/deny?username=<username>')
@app.route('/deny', methods=["POST", "GET"])
def deny():
    
    print('--------DENY TRIGGERED VIA EMAIL----------')
    username = request.args.get('username')
    user = json.loads(api_service.getGuestUserbasedOnName(username))

    if 'GuestUser' in user and 'ui_approve_text_label' in user['GuestUser']['customFields'] and user['GuestUser']['customFields']['ui_approve_text_label'] == 'waiting':
        
        #suspend user
        denyResponse = api_service.suspendGuestUserbyName(user['GuestUser']['name'])
        print(denyResponse)
        
        #inform guest user about approved request
        mail_service.sendMail(user['GuestUser'], 'guestDeny', '') 
                         
        return render_template("suspended.html", username=username)
    
    return render_template("invalidRequest.html")
    

'''
Route for checking for new approval requests users
'''
@app.route('/', methods=["POST", "GET"])
def backend():
    
    print('--------CHECKING FOR NEW REQUEST MANUALLY TRIGGERED----------')
    approvalRequestAvailable = sendApprovalMails()

    if approvalRequestAvailable == True:
        return render_template("emailSent.html")

    return render_template("noNewUsers.html")


'''
Retrieve the available sponsor portals and corresponding information (including ID)
'''
@app.route('/sponsorportals', methods=["GET"])
def sponsorPortals():
    
    print('--------RETRIEVING SPONSOR PORTALS----------')
    sponsorPortals = json.loads(api_service.getSponsorPortals())
    
    return render_template("sponsorPortals.html", sponsorPortals = sponsorPortals)



'''
Checking for new users and thereby approval requests. Informing sponsors about new request.
'''
def sendApprovalMails():

    print('-----------------SCANNING FOR UNAPPROVED REQUESTS-------------------------')

    users = api_service.getGuestUsers()
    
    for user in json.loads(users)['SearchResult']['resources']:
        
        detailUser = json.loads(api_service.getGuestUserbasedOnName(user['name']))

        if 'GuestUser' in detailUser and 'ui_approve_text_label' in detailUser['GuestUser']['customFields'] and detailUser['GuestUser']['customFields']['ui_approve_text_label'] == 'true':
            
            print(detailUser) 
            
            #update guestuser to have access for 14 days and approval state to 'waiting'             
            updateInfo = api_service.updateGuestUserByName(user['name'], 14, 'waiting')
            
            print(updateInfo)

            sponsorMail = detailUser['GuestUser']['personBeingVisited']

            #inform sponsor about new request
            mail_service.sendMail(detailUser['GuestUser'], 'sponsor', sponsorMail) 
            return True
        
    return False


def scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=sendApprovalMails, trigger="interval", seconds=SCHEDULER_INTERVAL_SEC)
    scheduler.start()
    

''' Starting Flask web application '''
if __name__ == "__main__":
    
    scheduler()
    
    port = int(os.environ.get("PORT", 8000))

    # Start the Flask web server
    app.run(host="0.0.0.0", port=port)