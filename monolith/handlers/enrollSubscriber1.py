import boto3
import os
import uuid
import json

DynamoDB_table_name = os.environ['TABLE_NAME']
region_name = os.environ['REGION']

def lambda_handler(event, context):
  print("Handler running!")
  try:
    print("in first try block")
    body = json.loads(event['body'])
    # Generate a unique ID for the new subscriber
    unique_id = str(uuid.uuid4())

    # Get the input information from the event (form submission) that was passed in
    fullName = body["fullName"]
    email = body["email"]
    phone = body["phone"]
    preferredLanguage = body["preferredLanguage"]
    state = body["state"]
    county = body["county"]
    message = f"Hello {fullName}. You have been subscribed!"
    
    print("************* Created Unique ID : " + unique_id)

    # Connect to DynamoDB service in your Region
    dynamodb = boto3.resource("dynamodb", region_name=region_name)
    table = dynamodb.Table(DynamoDB_table_name)

    # Put an Item to Table
    try:
      print("in second try block, table.putitem")
      table.put_item(
          Item={
              'id': unique_id,
              'fullName': fullName,
              'email': email,
              'phone': phone,
              'preferredLanguage': preferredLanguage,
              'state': state,
              'county': county
          }
      )
      print("Successfully Inserted a new subscriber with id : " + unique_id)
      
      response = {
              'statusCode': 500,
              'body': json.dumps({'error': 'Translation failed'})
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