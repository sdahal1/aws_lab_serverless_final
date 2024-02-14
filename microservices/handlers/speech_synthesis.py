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
    print("*************RECIEVED DATA FROM SYNTHESIS QUEUE " + unique_id + " " + preferredLanguage + " " + message + " " + email)
    presigned_url = synthesize_message(message, preferredLanguage, region_name)

    if presigned_url is None:
        errorResponse = {
            'statusCode': 500,
            'body': json.dumps({'error': 'Synthesis failed'})
        }
        return errorResponse
    
    print("Synthesized message to this", presigned_url)
    # Call the next sqs queue to send the synthesized message to the email service
    sqs = boto3.client('sqs')
    queue_url = os.environ['EMAIL_QUEUE_URL']
    try:
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps({
                'id': unique_id,
                'fullName': fullName,
                'preferredLanguage': preferredLanguage,
                'email': email,
                'message': message,
                'presigned_url': presigned_url
            })
        )
        print("Successfully sent a message to email queue")
    except Exception as e:
        print("Send message to SQS failed because ", e)
        response = {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to send message to queue', 'details': str(e)})
        }
        return response
   
    response = {
        'statusCode': 200,
        'body': json.dumps({'message': 'Success from speech synthesis lambda! ' + presigned_url})
    }
    return response



def synthesize_message(message, preferredLanguage, region_name):
    # Print a message indicating that the function is running
    print('running polly')

    # Define a dictionary mapping language codes to Polly voice names
    languageVoices = {
        "ar": "Zeina",
        "ca": "Arlet",
        "zh": "Zhiyu",
        "da": "Naja",
        "nl": "Ruben",
        "en": "Joanna",
        "fi": "Suvi",
        "fr": "Mathieu",
        "de": "Marlene",
        "hi": "Aditi",
        "is": "Karl",
        "it": "Bianca",
        "ja": "Mizuki",
        "ko": "Seoyeon",
        "no": "Liv",
        "pl": "Ewa",
        "pt": "Camila",
        "pt-PT": "Ines",
        "ro": "Carmen",
        "ru": "Tatyana",
        "es": "Conchita",
        "es-MX": "Mia",
        "sv": "Astrid",
        "tr": "Filiz",
        "cy": "Gwyneth"
    }

    try:
        # Create an Amazon Polly client and an S3 clientt
        polly = boto3.client('polly', region_name=region_name)
        s3 = boto3.client('s3')

        # Synthesize speech from the input message using the specified language and voice
        response = polly.synthesize_speech(
            Text=message,
            VoiceId=languageVoices[preferredLanguage],  # Get the voice based on the preferred language
            OutputFormat='mp3'
        )

        # Get the audio stream from the response
        audio_stream = response['AudioStream']

        # Save the audio stream to an S3 bucket
        unique_id = str(uuid.uuid4())
        s3_key = f"{unique_id}.mp3"
        s3_bucket_name = os.environ['VOICE_AUDIO_BUCKET']
        s3.put_object(
            Bucket=s3_bucket_name,
            Key=s3_key,
            Body=audio_stream.read(),
            ContentType='audio/mpeg'
        )

        # Generate a pre-signed URL for the uploaded audio file
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': s3_bucket_name, 'Key': s3_key},
            ExpiresIn=3600  # URL expiration time in seconds (adjust as needed)
        )

        # Return the pre-signed URL
        return presigned_url
    except Exception as e:
        # Print an error message if an exception occurs
        print("Failed to generate audio message:", e)
        return None