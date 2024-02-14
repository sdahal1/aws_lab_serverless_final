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
            
            # CALL ON TRANSLATE MESSAGE FUNCTION AND TRANLATE MESSAGE TO PREFERRED LANGUAGE
            message = f"You have been subscribed for emergency notifications, {fullName} at the state of {state}"
            translated_message = translate_message(message, preferredLanguage)
            # HANDLE TRANSLATION FAILURE - RETURN ERROR RESPONSE
            if translated_message is None:
                errorResponse = {
                    'statusCode': 500,
                    'body': json.dumps({'error': 'Translation failed'})
                }
                return errorResponse
            
            else:
                response = {
                        'statusCode': 200,
                        'body': json.dumps({'success': translated_message}) # 3. RETURN THE TRANSLATED MESSAGE
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


# 1. CREATE A FUNCTION TO TRANSLATE THE MESSAGE
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