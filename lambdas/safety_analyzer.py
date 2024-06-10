import json
import logging
import os
from decimal import Decimal

import boto3


def handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ["ANALYSIS_RESULTS_TABLE"])
    # {'Records': [{'messageId': 'b6c9c6cc-7f33-4b29-8548-72884427cf0b', 'receiptHandle': 'AQEBl/P+9wpAVFxk5TUXVZH834Biqca7H1bLoMG1lAD6kiVc/hEEz7Nqb6HBdqbOK81Ci94M5hvOXFgsrbzpKNj6FxocOmnrn/2FUqiepJZnoGmODTT/D5fkx69d7EQmVSkEj8CtHB3j802MuTutaHS1F/e0yFH7iaK1z3AYJlAUZ9opFYnhDJBSt9QJVtjI2RX58sm1rK6UpAfmo2VucTDkC78pyzS1zO3gM1h9Uchtc8uqV0BHQ8MlNZKX0UicGtF2aqjq18OCAC6I9fbbJXQieRG0OWrtecKoatg5a2UWWqYW9byEgwUPhwuh/uJLd9yuBEq2tO6iTEtXxtH99RFN+Wyk+oBFXYCAEqgAfUcKR/V92qsouA+RyURfGkPJd8WhijHPo/23sZwHVP+lscm3oks/QifksyUwZstLQZjIpp9e72M5nnHkaxZMFTWQgUN7FsoUbqRbFH5jCNbSorzKwQ==', 'body': 
    #   '{
    #       "type": "app_mention", 
    #       "user": "U1234567890", 
    #       "text": "Hey, can you help me with something?", 
    #       "ts": "1623456789.001234", 
    #       "channel": "C1234567890", 
    #       "event_ts": "1623456789.001234"
    #   }', 'attributes': {'ApproximateReceiveCount': '1', 'AWSTraceHeader': 'Root=1-66668e2a-5df7ce5d090095a777c17c2c;Parent=5d5f84097647f4fe;Sampled=0;Lineage=0ad24ca9:0', 'SentTimestamp': '1717997098751', 'SenderId': 'AROA35LLXVSMDOVW7BSTP:Deploy-SlackGuardianWebServ-EventProcessorD4153CB5-3tNmcbth0zn4', 'ApproximateFirstReceiveTimestamp': '1717997098756'}, 'messageAttributes': {}, 'md5OfBody': '8adc2c1f9aa2a741d26b63ccb75d63f0', 'eventSource': 'aws:sqs', 'eventSourceARN': 'arn:aws:sqs:us-east-1:818954087576:Deploy-SlackGuardianWebService-SlackEventQueueB8EA9EE1-IsVfJCXs3Vpf', 'awsRegion': 'us-east-1'}]}
    for record in event['Records']:
        message_body = json.loads(record['body'])

        # Perform safety analysis on the message_body
        # ...
        analysis_result = {
            # ... analysis result ...
            "hello": "world",
        }

        # Convert Timestamp to Decimal
        timestamp = Decimal(str(message_body.get('ts', 0)))

        # Store analysis result in DynamoDB
        try:
            table.put_item(
                Item={
                    'MessageId': message_body.get('event_ts', 'unknown_timestamp'),  # Use event_ts as unique ID
                    'Timestamp': timestamp,
                    'AnalysisResult': json.dumps(analysis_result),
                    'Channel': message_body.get('channel', 'unknown_channel'),
                    'User': message_body.get('user', 'unknown_user'),
                    'MessageContent': message_body.get('text', '')  # Optional
                }
            )
        except Exception as e:
            logging.error(f"Error storing analysis result in DynamoDB: {e}")
            return

        # Take actions based on the analysis
        # ...
        _lambda = boto3.client('lambda')
        resp = _lambda.invoke(
            FunctionName=os.environ['ACTION_HANDLER_FUNCTION_NAME'],
            Payload=json.dumps(analysis_result),
        )