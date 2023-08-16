import base64
import json
import smtplib
import requests
from google.cloud import secretmanager
from json import loads
from email.utils import formataddr


def hello_pubsub(event, context):
    # Secret Manager credentials loading
    secret_client = secretmanager.SecretManagerServiceClient()
    project_id = "sandydev"
    secret_response = secret_client.access_secret_version(
        {"name": "projects/"+project_id+"/secrets/dlp_data/versions/latest"}
    )
    secret_response = secret_response.payload.data.decode("utf-8")
    my_credentials = loads(secret_response)

    # ServiceNow credentials fetched
    servicenow_user = my_credentials["user"]
    servicenow_password = my_credentials["pwd"]

    # SMTP server credentials fetched
    smtp_email = my_credentials["serv_mail"]
    smtp_password = my_credentials["password"]

    # Pub/Sub topic data loading
    pubsub_message = base64.b64decode(event["data"]).decode("utf-8")
    message_json = json.loads(pubsub_message)

    # Write the record to ServiceNow incident table
    url = "https://dev125963.service-now.com/api/now/table/incident"

    # Set credentials for ServiceNow API
    user = servicenow_user
    pwd = servicenow_password

    # Set proper headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Create the incident data
    incident_data = {
    "short_description": "Alert PII Information Detected",
    "description": f'''
        The below details are flagged as PII information by DLP Service and are encrypted by the DLP Job running in GCP:

        - Duration: {message_json["duration"]} seconds

        - Text: {message_json["text"]}

        - Audio Name : {message_json["audio_file_name"]}

    ''',
    "urgency": "1",
    "impact": "1",
    "priority": "1",
    "category": "Data Privacy",
    "subcategory": "Sensitive Information",
    "caller_id": "sandeep.mohanty1998@gmail.com",
    "assigned_to": "sandeepdev751@gmail.com",
}

    # Do the HTTP request to create the incident
    try:
        response = requests.post(
            url, auth=(user, pwd), headers=headers, json=incident_data
        )
        response.raise_for_status()
        incident_response = response.json()  # Parse the response JSON
        incident_number = incident_response.get("result", {}).get("number")  # Extract the incident number
        print("Incident created successfully. Incident Number:", incident_number)
    except requests.exceptions.RequestException as e:
        print("Error creating incident:", str(e))

    email_subject_bigquery = "PII Information Detected!"
    email_body_bigquery = f'''
    Dear BigQuery Admin,

    We want to inform you that personally identifiable information (PII) has been detected in a transaction.

    - Duration: {message_json["duration"]} seconds

    - Text: {message_json["text"]}

    - Audio Name : {message_json["audio_file_name"]}

    Appropriate actions has been taken by the DLP teammsecure the data.

    Thank you,
    DataLake DLP Admin Team,
    sush Ltd.
    '''
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(smtp_email, smtp_password)
            sender_name = "DLP DataLake Admin Team"
            sender_address = "no-reply@dlpadmin.com"
            formatted_sender = formataddr((sender_name, sender_address))
            email_message_bigquery = f"From: {formatted_sender}\nSubject: {email_subject_bigquery}\nTo: sandeep.mohanty1998@gmail.com\n\n{email_body_bigquery}"
            server.sendmail(smtp_email, "sandeep.mohanty1998@gmail.com", email_message_bigquery)
            
        print("Emails sent successfully.")
    except Exception as e:
        print("Error sending emails:", str(e))


    print(pubsub_message)
