import json
import logging
import os
from decimal import Decimal

import boto3
from openai import OpenAI


CONCERN_NONE = "No safety concerns identified."

analyzer_specification = """
You are a safety management assistant. Analyze the following Slack message for potential safety concerns, including bullying/harassment, sharing of sensitive information, mental health issues, or signs of a crisis/emergency. 

Consider the following factors:

* Message content: Pay close attention to the words and phrases used in the message.
* Sentiment: Assess the overall emotional tone of the message (positive, negative, neutral).
* Context: Consider the channel or conversation in which the message was sent.
* Author: If available, consider any relevant information about the author of the message (e.g., role, history).

Based on your analysis, provide a summary of any potential safety concerns you identify and suggest an appropriate action to take. If no concerns are found, indicate that the message appears to be safe. 

Example Output:
* Concern: [Type of concern]
* Evidence: [Relevant excerpts from the message]
* Suggested Action: [Specific action to take, e.g., alert HR, notify security, offer support]

If no concerns are found, simply state "No safety concerns identified."
"""

openai_secret_key_arn = os.environ['OPENAI_SECRET_KEY_ARN']
secrets_client = boto3.client("secretsmanager")

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ["ANALYSIS_RESULTS_TABLE"])

_lambda = boto3.client('lambda')

# ChatCompletionMessage(
#   content='* Concern: Potential crisis/emergency \n* 
#              Evidence: The message indicates a person in a potentially dangerous situation, standing on the edge of a bridge.\n* 
#              Suggested Action: Immediately call emergency services (911 or relevant emergency number) to report the situation and provide details about the location and the individual in distress. Keep the person engaged in conversation and try to prevent them from taking any drastic actions until help arrives.', 
#   role='assistant', 
#   function_call=None, tool_
#   calls=None
# )
# ChatCompletionMessage(content='No safety concerns identified.', role='assistant', function_call=None, tool_calls=None)

def handler(event, context):
    get_secret_value_response = secrets_client.get_secret_value(SecretId=openai_secret_key_arn)
    openai_secret_key = get_secret_value_response['SecretString']

    openai_client = OpenAI(
        api_key=openai_secret_key,
    )

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

        analysis_result = CONCERN_NONE
        try:
            completion = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": analyzer_specification.strip()},
                    {"role": "user", "content": message_body.get("text", "")}
                ]
            )
            analysis_result = completion.choices[0].message.content
            print("CHATGPT result:\n", analysis_result)
        except Exception as e:
            print("Error analyzing message:", e)
            continue

        timestamp = Decimal(str(message_body.get('ts', 0)))

        # Store analysis result in DynamoDB
        try:
            table.put_item(
                Item={
                    'MessageId': message_body.get('event_ts', 'unknown_timestamp'),  # Use event_ts as unique ID
                    'Timestamp': timestamp,
                    'AnalysisResult': analysis_result,
                    'Channel': message_body.get('channel', 'unknown_channel'),
                    'User': message_body.get('user', 'unknown_user'),
                    'Message': json.dumps(message_body),
                }
            )
        except Exception as e:
            logging.error(f"Error storing analysis result in DynamoDB: {e}")
            continue

        if analysis_result.strip() == CONCERN_NONE:
            continue

        # Take actions based on the analysis
        # ...
        print("BEFORE INVOKING ACTION HANDLER FUNCTION")
        try:
            _lambda.invoke(
                FunctionName=os.environ['ACTION_HANDLER_FUNCTION_NAME'],
                Payload=json.dumps({"text": analysis_result}),
            )
            print("AFTER INVOKING ACTION HANDLER FUNCTION")
        except Exception as e:
            print("Error invoking action handler function:", e)