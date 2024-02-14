import boto3
import os
import uuid
import json



def lambda_handler(event, context):
    print("Handler for send_email running!")
    body = json.loads(event['Records'][0]['body'])
    id = body['id']
    preferredLanguage = body['preferredLanguage']
    email = body['email']
    message = body['message']
    presigned_url = body['presigned_url']
    fullName = body['fullName']
    print("*************RECIEVED DATA FROM EMAIL QUEUE " + id + " " + preferredLanguage + " " + email + " " + message + " " + presigned_url);
    # Call the send_email function to send the email to the subscriber
    responseFromEmail = send_email(fullName, [email], message, presigned_url)
    if responseFromEmail == "Error":
        errorResponse = {
            'statusCode': 500,
            'body': json.dumps({'error': 'Email failed to send'})
        }
        return errorResponse
    
    print("Email sent successfully")
    response = {
        'statusCode': 200,
        'body': json.dumps({'message': 'Success from email send lambda!'})
    }
    return response

# ADD THE SEND EMAIL FUNCTION
def send_email(fullName, emails, message, audio_url):
  VERIFIED_EMAIL = os.environ['VERIFIED_EMAIL']
  ses = boto3.client('ses')
  try:
    response = ses.send_email(
      Source=VERIFIED_EMAIL,
      Destination={
          'ToAddresses': emails  # An array of verified emails if in sandbox mode
      },
      Message={
          'Subject': {'Data': 'You have a new notification'},
          'Body': {'Text': {'Data': f"Hello {fullName} You have a new message: {message}. \n Hear it in audio: {audio_url}"}}
      }
    )
    print('Email sent successfully:', response)
    return 'Success!'
  except Exception as e:
    print("Failed to send email:", e)
    return "Error"