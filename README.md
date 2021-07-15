### email_service
python email_service with django

# Models 

  - Receiver
    - *email* -  unique field
    - *name*\* - field can be useful for template
    - *lastname*\* - field can be useful for template
    - *bday*\* - date field can be useful for template  
     #### You can add some new fields if you have additional information about your receivers
  - MailingList
    - *mailinglist_name* - unique field
    - *receivers* - ManyToMany to Receiver
  - HtmlTemplate
    - *template_location* - expample.html in location email_service/template/mailing
    - *template_name*  - unique field
  - Mailing
    - *mailing_name* - unique field
    - *mailing_list* - ForeingKey to MailingList
    - *mailing_template* - ForeingKey to HtmlTemplate
    - *mailing_date* - date to start mailing, today(default)
    - *mailing_status* - True if mailing already been done
    - *mailing_subject*\* - field can be useful for template
    - *mailing_body*\* - field can be useful for template
    - *mailing_signature*\* - field can be useful for template
 - MailingReceiver - 
    - *mailing* - ForeingKey to Mailing
    - *receiver* - ForeingKey to Receiver
    - *send*\* - bool field, "True" when mail is send
    - *send_date*\* - datetime field
    - *received*\* - bool field, "True" when mail is received
    - *received_date*\* - datetime field
    
 \* can be null or empty

# 1. Receiver database interaction
   - email/
     - GET - return list of all emails in database 
     - GET ?email=search_object  show you all emails that consist search_object                                               
     - POST - request body {"email":"user@example.com", "name":"Boris", "lastname":"Borisov", "bday":"YYYY-MM-DD"}
     
   - emails/*email_id*/ 
     - GET - get email from database with *email_id* ID
     - POST - edit email from database with *email_id* ID
     - DELETE - delete email from database with *email_id* ID
     
 # 2. Mailing list interaction
   - mailing-list/
     - GET - return list of all mailing list in database 
     - GET ?mailinglistname=search_object  show you all mailing list that consist search_object                                             
     - POST - request body {"mailinglist_name":"Example name", "emails_pk": [pk_1, pk_2] OR "emails":[email_1, email_2]}
    
   - mailing-list/*mailing_list_id*/ 
     - GET - get mailing list from database with *mailing_list_id* ID
     - POST - edit mailing list from database with *mailing_list_id* ID
     - DELETE - delete mailing list from database with *mailing_list_id* ID
  
 # 3. Templates interaction
   - templates/
     - GET - return list of all templates in database                                            
     - POST - request body {"template_name":"Example templat name", "template_location": "example.html"}
    
   - templates/*templates_i*/ 
     - GET - get template from database with *template_id* ID
     - POST - edit template  from database with *template_id* ID
     - DELETE - delete mailing list from database with *template_id* ID
  
  # 4. Mailing interaction   
   - mailing/
     - GET - list of all mailing in database 
     - GET ?mailing_name=search_object  show you all mailing that consist search_object                                             
     - POST - request body {"mailing_name":"Example name", "maling_list": "mailing_list_id",  "mailing_template":"example_mailing_template",
     "mailing_date":"YYYY-MM-DD", "mailing_body":"example body", "mailing_signature":"example signature"}
    
   - mailing/mailing_id/ 
     - GET - get mailing from database with mailingt_id ID
     - POST - edit mailing from database with mailing_id ID
     - DELETE - delete mailing from database with mailing_id ID
    
     #### If the mailing has already been done, a list of sent letters with additional information will also be displayed.
     
  # 5. The mailing starts at midnight. Use the following command to launch the available mailing today.
   - activate_mailing/ 
     - POST - starting all available today mailing

    
 # Launching instruction
 For easy lauching need **docker-compose**
 
 In *email_service/email_service/* edit **settings.py**
 
    PROJECT_DOMAIN = 'http://YOUR_IP_OR_DOMAIN:8000'
 
    EMAIL_HOST_USER='YOUR_EMAIL'
    EMAIL_HOST_PASSWORD='YOUR_PASSWORD'
 
 Start in project root folder:
 
    docker-compose build
    docker-compose up
      
  Project will be available on local machine on http://YOUR_IP_OR_DOMAIN:8000
