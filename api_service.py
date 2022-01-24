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

import datetime
import os
import requests
import base64
import json
from dotenv import load_dotenv

# load all environment variables
load_dotenv()

'''Global variables'''

'''ISE Instance'''
HOST = os.environ['HOST']

''' Setup ISE credintials '''
'''User ERS Admin credentials = normal ISE login user'''
ERS_USERNAME = os.environ['ERS_USERNAME']
ERS_PASSWORD = os.environ['ERS_PASSWORD']

ers_creds = str.encode(ERS_USERNAME+':'+ERS_PASSWORD)
ers_encodedAuth = bytes.decode(base64.b64encode(ers_creds))

ers_headers = {
'Content-Type': 'application/json',
'Accept': 'application/json',
'Authorization': 'Basic ' + ers_encodedAuth
}

'''Sponsor Account credentials =  Admin > identities > users'''
SPONSOR_USERNAME = os.environ['SPONSOR_USERNAME']
SPONSOR_PASSWORD = os.environ['SPONSOR_PASSWORD']

sponsor_creds = str.encode(SPONSOR_USERNAME +':'+ SPONSOR_PASSWORD)
sponsor_encodedAuth = bytes.decode(base64.b64encode(sponsor_creds))

sponsor_headers = {
'Content-Type': 'application/json',
'Accept': 'application/json',
'Authorization': 'Basic ' + sponsor_encodedAuth
}


'''Sponsor Portal Info'''
SPONSOR_PORTAL_ID = os.environ['SPONSOR_PORTAL_ID']


'''Create Timestamps based on number of days'''
def getDates(days):
    # get current date
    fromDateObject = datetime.datetime.now()
   
    #get days to date python lib object
    delta = datetime.timedelta(days=days)
    toDateObject = fromDateObject + delta

    # format as mm/dd/y
    fromDate = fromDateObject.strftime("%m/%d/%Y %H:%M")
    toDate = toDateObject.strftime("%m/%d/%Y %H:%M")

    return fromDate, toDate


'''
Update a guest user by its username.
'''
def updateGuestUserByName(name, days, approveStatus):

    print('-------------UPDATE GUEST USER BY NAME: '+ name +'-------------------')
    

    fromDate, toDate = getDates(days)

    payload = {
        "GuestUser" : {
            "guestType" : "Contractor (default)",
            "guestInfo" : {
        },
        "guestAccessInfo" : {
            "validDays" : days,
            "fromDate" : fromDate,
            "toDate" : toDate
            },
            "portalId" : SPONSOR_PORTAL_ID,
            "customFields" : {
                "Approve" : approveStatus
                }
            }
        }
    
    url = HOST +":9060/ers/config/guestuser/name/" + name
    method = "PUT"
    response = requests.request(method, url, headers=sponsor_headers, data=json.dumps(payload), verify=False)
    print('Response Code: ' + str(response.status_code))
    return response.text


'''
Update a guest user by its ID.
'''
def updateGuestUserByID(userID, days):
    
    print('---------------UPDATE GUEST USER BY ID: '+ userID +' --------------------')

    fromDate, toDate = getDates(days)

    payload = {
        "GuestUser" : {
            "guestType" : "Contractor (default)",
            "guestInfo" : {
        },
        "guestAccessInfo" : {
            "validDays" : days,
            "fromDate" : fromDate,
            "toDate" : toDate
            },
            "portalId" : SPONSOR_PORTAL_ID
            }
        }
    
    url = HOST +":9060/ers/config/guestuser/"+ userID
    method = "PUT"
    response = requests.request(method, url, headers=sponsor_headers, data=json.dumps(payload), verify=False)
    print('Response Code: ' + str(response.status_code))
    return response.text


'''
Suspend a guest user by username
'''
def suspendGuestUserbyName(username):
    print('------------SUSPENDED GUEST USER: '+ username +' -------------')
    url = HOST +":9060/ers/config/guestuser/suspend/name/"+ username
    method = "PUT"
    response = requests.request(method, url, headers=sponsor_headers, data={}, verify=False)
    print('Response Code: ' + str(response.status_code))
    #print(response.text)
    return response.text


'''
Get all guest Users
'''
def getGuestUsers():
    print('-------------------GET ALL GUEST USERS-------------------')
    url = HOST +":9060/ers/config/guestuser"
    method = "GET"
    response = requests.request(method, url, headers=sponsor_headers, data={}, verify=False)
    print('Response Code: ' + str(response.status_code))
    return response.text

'''
Get detailed guest user info based on username.
'''
def getGuestUserbasedOnName(name):
    print('------------------GET GUEST USER BY USERNAME: '+ name +'--------------')
    url = HOST +":9060/ers/config/guestuser/name/" + name
    method = "GET"
    response = requests.request(method, url, headers=sponsor_headers, data={}, verify=False)
    print('Response Code: ' + str(response.status_code))
    return response.text


'''
Get detailed guest user info based on ID.
'''
def getGuestUserByID(userID):
    print('---------------GET GUEST USER BY ID: '+ userID +'--------------------')
    url = HOST +":9060/ers/config/guestuser/" + userID
    method = "GET"
    response = requests.request(method, url, headers=sponsor_headers, data={}, verify=False)
    print('Response Code: ' + str(response.status_code))
    #print(response.text)
    return response.text

'''
Get all sponsor portals
'''
def getSponsorPortals():
    print('-----------------GET SPONSOR PORTALS----------------')
    url = HOST +":9060/ers/config/sponsorportal"
    method = "GET"
    response = requests.request(method, url, headers=ers_headers, data={}, verify=False)
    print('Response Code: ' + str(response.status_code))
    return response.text


