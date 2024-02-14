import boto3
import os
import uuid
import json

region_name = os.environ['REGION']


def lambda_handler(event, context):
    print("Handler for translate_message running!")
    queuedMessage = json.loads(event['Records'][0]['body'])
    unique_id = queuedMessage['id']
    preferredLanguage = queuedMessage['preferredLanguage']
    message = queuedMessage['message']
    email = queuedMessage['email']
    fullName = queuedMessage['fullName']
    print("*************RECIEVED DATA FROM TRANSLATION QUEUE " + unique_id + " " + preferredLanguage + " " + message + " " + email)
    translated_message = translate_message(message, preferredLanguage)

    if translated_message is None:
        errorResponse = {
            'statusCode': 500,
            'body': json.dumps({'error': 'Translation failed'})
        }
        return errorResponse
    
    print("translated message to this", translated_message)
    # Call the next sqs queue to send the translated message to the speech synthesis service
    sqs = boto3.client('sqs')
    queue_url = os.environ['SYNTHESIS_QUEUE_URL']
    try:
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps({
                'id': unique_id,
                'fullName': fullName,
                'preferredLanguage': preferredLanguage,
                'message': translated_message,
                'email': email
            })
        )
        print("Successfully sent a message to synthesis queue")
    except Exception as e:
        print("Send message to SQS failed because ", e)
        response = {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to send message to queue', 'details': str(e)})
        }
        return response
            


def translate_message(message, target_language):
    translate = boto3.client('translate')
    try:
        response = translate.translate_text(
            Text=message,
            SourceLanguageCode='en-US',
            TargetLanguageCode=target_language
        )
        translated_message = response['TranslatedText']
        print("Successfully translated message")
        return translated_message
    except Exception as e:
        print("Translation failed:", e)
        return None