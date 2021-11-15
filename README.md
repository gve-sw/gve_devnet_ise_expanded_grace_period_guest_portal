# ISE - Expanded Grace Period Guest Portal
The expanded grace period guest portal enhances the ISE Self-Registration Guest Portal to allow a grace period longer than 30 min for sponsors to approve a new guest user. Furthermore, it allows the browser window to be closed after the self-registration and automatically connects the guest user to the network after successful registration. ISE instead requires the browser window to stay open while waiting for approval.


## Contacts
* Ramona Renner

## Solution Components
* Cisco ISE (Identity Services Engine) with admin access
* Two email accounts

## Demo Workflow

![/IMAGES/workflow.png](/IMAGES/workflow.png)

### High-Level Architecture

![/IMAGES/overview.png](/IMAGES/overview.png)


A native ISE self-registration portal covers the creation of a guest user account with 2 weeks validity on successful registration. 

The guest application handles the whole approval process. Therefore, it checks every 20 seconds (interval is adjustable) for new users for whom the approval process has not yet been started. These users are characterized by the value true of a hidden custom field (Approve) in the self-registration form. 
As soon as a new guest user successfully registers via the self-registration portal, the application will identify the user and start the following approval process based on the mentioned field value:
1. Request detailed information about the identified new user
2. Change custom field (Approve) to waiting
3. Request detailed information about the endpoint associated with the session of the user 
4. Assign endpoint to predefined short-term endpoint group
5. Trigger change of authorization to reauthenticate the endpoint
6. Send approval request email to sponsor
7. Sponsor triggers the action to accept or deny by clicking the corresponding link in the email.   
7.1. Accept:  
7.1.1. Update guest user's account validity to 180 days and change custom field (Approve) to approved  
7.1.2. Request detailed information about the endpoint associated with the session of the user  
7.1.3. Assign endpoint to predefined long-term endpoint group  
7.1.4. Trigger change of authorization to reauthenticate the endpoint  
7.2. Deny:  
7.2.1. Suspend user from network  
8. Send approval result email to guest user  



## Installation/Configuration

### ISE Setup

This demo builds on a self-registration guest portal and a sponsor portal in ISE. Please check out the official ISE documentation for information on how to set up and use the mentioned portals or use the default portals.

Configure the following steps after the basic portal setup to prepare ISE for this demo. Feel free to skip steps that are already configured in ISE:

1. **Add user location to ISE:** Go to: Work Centers > Guest Access > Settings > Guest Locations and SSIDs > Fill in **Location name** (e.g. San Jose) > Choose **Time zone** (e.g. America/Los_Angeles) > Click **Add** > Click: **Save**
  ![/IMAGES/locations.png](/IMAGES/locations.png)

2. **Create two custom fields in ISE:** Go to: Work Centers > Guest Access > Settings > Custom Fields > Fill in **Custom field name** > Choose **Data type** > Click **Add** > Click: **Save**
  
* Customer field 1: Name: Approve, Type: String
* Customer field 2: Name: SessionID, Type: String

  ![/IMAGES/createCustomField.png](/IMAGES/createCustomField.png) 
  

On the preferred Self-Registration Guest Portal page (under Work Centers > Guest Access > Portals & Components > [Preferred Self-Registration Guest Portal]):  

3. **Allow guests to create their own accounts:** Go to: ... > Portal Behavior and Flow Settings -> Login Page Settings > Check: Allow guests to create their own accounts  
  ![/IMAGES/allowCreateAccounts.png](/IMAGES/allowCreateAccounts.png)

4. **Set account validity to 14 days and guest type to Contractor (default):** Go to: ... > Portal Behavior and Flow Settings -> Registration Form Settings > Set: Assign to guest type **Contractor (default)** and Account valid for **14 Days**  
  ![/IMAGES/validity.png](/IMAGES/validity.png)

5. **Add custom fields to the self-registration form:** Go to: ... > Portal Behavior and Flow Settings -> Registration Form Settings > Fields to include > Click: **Custom Fields** > Select preferred custom fields (Approve and SessionID) > Click **OK**  
  ![/IMAGES/addCustomField.png](/IMAGES/addCustomField.png)
  ![/IMAGES/addCustomField2.png](/IMAGES/addCustomField2.png)  

6. **Define the self-registration form fields:** Go to: ... > Portal Behavior and Flow Settings -> Registration Form Settings > Check the following fields 

  * First name 	
  * Last name 
  * Email address
  * Company 
  * Location (add location as decribed in step 1 beforehand e.g. San Jose)
  * Person being visited
  * Approve (add custom field as described in step 5 beforehand)
  * SessionID (add custom field as described in step 5 beforehand)

  ![/IMAGES/formfields.png](/IMAGES/formfields.png)

7. **Disable grace access option:** Go to: ... > Portal Behavior and Flow Settings -> Registration Form Settings > Uncheck: Require guest to be approved      
  ![/IMAGES/disableGraceAccess.png](/IMAGES/disableGraceAccess.png)

8. Save all changes in the **Portal Behavior and Flow Settings** tab by clicking **Save** 

9. **Add a script to hide the custom fields and set their value - approve: true; sessionID: id shared in URL:** True indicates a new guest user for whom the approval process has not yet been started. Go to: ... > Portal Page Customization >      
  
  Registration Form > Add the following in the  **Optional Content 2** field > Click: **Save**:   
  ```python 
  <script type="text/javascript">
    $('input[id="guestUser.fieldValues.ui_approve_text"]').attr('value', 'true');
    $('label[for="guestUser.fieldValues.ui_approve_text"]').parent().hide();
    
    //Get url
    var url= window.location.href;
    var session_id = url.split('sessionId=').pop().split('&')[0];
    
    $('input[id="guestUser.fieldValues.ui_sessionid_text"]').attr('value', session_id );
    $('label[for="guestUser.fieldValues.ui_sessionid_text"]').parent().hide();
  </script>
  ```

  Self-Registration Success > Add the following in the  **Optional Content 2** field > Click: **Save**:  

  ```python
  <script type="text/javascript">
      $('div.ui_reg_succ_approve_text_label').hide();
      $('div.ui_reg_succ_sessionid_text_label').hide();
  </script>
  ```
  
  > Note: Please switch to code mode before adding code in the Optional Content 2 field and switch to normal mode before saving your changes ![/IMAGES/optionalContent.png](/IMAGES/optionalContent.png)  

  > Note: Choose the portal page language for which you want to add the js code beforehand  ![/IMAGES/language.png](/IMAGES/language.png)

9. **Enable API use:** Follow the [instructions to enable the ISE ERS (External RESTful Services) APIs](https://developer.cisco.com/docs/identity-services-engine/3.0/#!setting-up) to:  
  9.1. Enable ERS (port 9060)  
  9.2. Create ERS Admin  
  9.3. Set up ERS for Sponsor Access  

10. **Verify the monitoring node:** Follow the [instructions to verify a monitoring node](https://developer.cisco.com/docs/identity-services-engine/3.0/#!introduction-to-monitoring-rest-apis/verifying-a-monitoring-node) to:  
  10.1. Go to: Administration > System > Deployment  
  10.2. Check that the target node you want to monitor is listed as a monitoring node  


### Guest Application Setup

1. Make sure you have [Python 3.8.0](https://www.python.org/downloads/) and [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) installed

2. Clone this Github repository into a local folder:  
  ```git clone [add github link here]```
  - For Github link: 
      In Github, click on the **Clone or download** button in the upper part of the page > click the **copy icon**  
      ![/IMAGES/giturl.png](/IMAGES/giturl.png)
  - Or simply download the repository as zip file using 'Download ZIP' button and extract it

3. Access the downloaded folder:  
  ```cd GVE_DevNet_ISE_Expanded_Grace_Period_Guest_Portal```

4. Install all dependencies:  
  ```pip install -r requirements.txt```

5. The App can be deployed on-prem or on different IaaS platforms like Heroku, Amazon Web Services Lambda, Google Cloud Platform (GCP) and more. In case the approve/deny action is triggered in the same network as the application is running, feel free to skip this step. Otherwise, the application requires to be reachable over an internet accessible URL. For this demo we use the tool Packetriot for this reason.
Download and configure [Packetriot](https://docs.packetriot.com/quickstart/):    

  ```python
  pktriot configure (do once, follow wizard steps to get hostname of tunnel)
  pktriot http 8000 --webroot ./assets 
  ```

6. Configure the environment variables in **.env** file:  
      
  ```python  
    HOST: https://[ISE hostname/IP]​
    ISE_PRIVATE_IP= [Private ISE IP]

    ERS_USERNAME: [ISE username]  ​
    ERS_PASSWORD: [ISE password]​  

    SPONSOR_USERNAME: [username of internal user for sponsor access. See step 9.3: Set up ERS for Sponsor Access]​  
    SPONSOR_PASSWORD: [password for internal user for sponsor access. See step 9.3: Set up ERS for Sponsor Access] 
    ​ 
    SPONSOR_PORTAL_ID: [ID of associated sponsor portal - see hint on how to easily retrieve the ID]​  

    USER_LOCATION: [user location (e.g.: San Jose)]​  

    SENDER_EMAIL: [email address from which notification emails will be send]​ 
    SENDER_PW: [password of sender email address account]
    ​  
    APP_URL: [tunnel hostname or http://localhost:8000, see step 5]​ 

    SCHEDULER_INTERVAL_SEC = [Interval in which script checks for new users] 

    SHORT_TERM_ENDPOINT_GROUP= [ID of endpoint group for short-term guest user] 
    LONG_TERM_ENDPOINT_GROUP= [ID of endpoint group for long-term guest user]  
  ```

> Note: Make sure that the sender email account settings allow the sending of emails via an external app (e.g. [Instructions for gmail.com account](https://www.google.com/settings/security/lesssecureapps) - Use only for testing purposes.)  

> Hint: Get a list of all available sponsor portals and their associated IDs by accessing localhost:8000/sponsorportals via the browser after starting the application without a set sponsor portal id environment variable.
 
7. Run application  
  ```python app.py```

At this point everything is set up and the application is running. Add a new user in the ISE self-registration portal to trigger the approval process. Log into the guest user and sponsor email account to retrieve and react to the emails send by the guest application. Monitor the changes within ISE in the associated sponsor portal.

## More Useful Resources

 - [Cisco ISE API Documentation](https://developer.cisco.com/docs/identity-services-engine/3.0/#!cisco-ise-api-documentation)
 - [Cisco ISE ERS API Examples](https://community.cisco.com/t5/security-documents/ise-ers-api-examples/ta-p/3622623)
 - [Cisco ISE Monitoring REST API](https://developer.cisco.com/docs/identity-services-engine/3.0/#!introduction-to-monitoring-rest-apis)

### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.