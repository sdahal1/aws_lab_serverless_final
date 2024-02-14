import boto3
import os
import uuid
import json

DynamoDB_table_name = os.environ['TABLE_NAME']
region_name = os.environ['REGION']

def lambda_handler(event, context):
    print("Handler running!")
    try:
        print("we are in first try")
        body = json.loads(event['body'])
        unique_id = str(uuid.uuid4())

        fullName = body["fullName"]
        email = body["email"]
        phone = body["phone"]
        preferredLanguage = body["preferredLanguage"]
        state = body["state"]
        county = body["county"]
        message = f"Hello {fullName}. You have been subscribed!"
        
        print("************* Created Unique ID : " + unique_id)

        dynamodb = boto3.resource("dynamodb", region_name=region_name)
        table = dynamodb.Table(DynamoDB_table_name)

        try:
            table.put_item(
                Item={
                    'id': unique_id,
                    'fullName': fullName,
                    'email': email,
                    'phone': phone,
                    'preferredLanguage': preferredLanguage,
                    'state': state,
                    'county': county,
                }
            )
            print("Successfully Inserted a new subscriber with id : " + unique_id)
            
            message = f"You have been subscribed for emergency notifications, {fullName} at the state of {state}"
            translated_message = translate_message(message, preferredLanguage)

            if translated_message is None:
                errorResponse = {
                    'statusCode': 500,
                    'body': json.dumps({'error': 'Translation failed'})
                }
                return errorResponse
            
            else:
                # Call the synthesize_message function to generate an audio URL for the translated message
                audio_url = synthesize_message(translated_message, preferredLanguage, region_name)

                # Check if the audio URL was successfully generated
                if audio_url is None:
                    # If the audio conversion failed, return an error response
                    response = {
                        'statusCode': 500,
                        'body': json.dumps({'error': 'Audio conversion failed'})
                    }
                    return response
                else:
                    # If the audio URL was successfully generated, print a success message
                    print("got the audio_url!!!", audio_url)
                    
                    # CALL THE SEND EMAIL FUNCTION
                    send_email(fullName, [email], translated_message, audio_url)
                    # Create a success response with the translated message and the audio URL
                    response = {
                        'statusCode': 200,
                        'body': json.dumps({'message': 'Success!', 'translated_message': translated_message, 'audio_url': audio_url})
                    }
                    return response
            
        except Exception as e:
            print("Insert Item to Table failed because ", e)
            response = {
                'statusCode': 500,
                'body': json.dumps({'error': 'Failed to insert item to table', 'details': str(e)})
            }
            return response
            
    except Exception as e:
        print("Connect to DynamoDB failed because ", e)
        response = {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to connect to DynamoDB', 'details': str(e)})
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
    

# Define a function to synthesize a message using Amazon Polly and save the audio to an S3 bucket.

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