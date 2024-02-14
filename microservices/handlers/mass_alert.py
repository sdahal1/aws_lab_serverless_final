import boto3
import os
import uuid
import json
from boto3.dynamodb.conditions import Attr

DynamoDB_table_name = os.environ['TABLE_NAME']
region_name = os.environ['REGION']

# def lambda_handler(event, context):
#   print("running lambda!!!!")
#   return {"statusCode":200, "body": json.dumps({"message": "Success"})}
def lambda_handler(event, context):
    print("Handler running!")
    try:
        body = json.loads(event['body'])
        
        message = body["message"]
        state = body["state"]
        # Connect to DynamoDB service in your Region
        dynamodb = boto3.resource("dynamodb", region_name=region_name)
        table = dynamodb.Table(DynamoDB_table_name)

        # Scan the table to get all users from the given state
        response = table.scan(
          FilterExpression=Attr('state').eq(state)
        )
        users = response['Items']
        print("************* Users from california in the table : ", users)
        # loop through all users and get their id, fullName, preferredLanguage, email
        for user in users:
            unique_id = user['id']
            fullName = user['fullName']
            preferredLanguage = user['preferredLanguage']
            email = user['email']
            print("************* User : ", unique_id, fullName, preferredLanguage, email)
            # Call the next sqs queue to send the synthesized message to the email service
            sqs = boto3.client('sqs')
            queue_url = os.environ['TRANSLATE_QUEUE_URL']
            try:
                sqs.send_message(
                    QueueUrl=queue_url,
                    MessageBody=json.dumps({
                        'id': unique_id,
                        'fullName': fullName,
                        'preferredLanguage': preferredLanguage,
                        'message': message,
                        'email': email
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
    except Exception as e:
        print("Connect to DynamoDB failed because ", e)
        response = {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to connect to DynamoDB', 'details': str(e)})
        }
        return response
        