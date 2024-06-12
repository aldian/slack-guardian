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


def handler(event, context):
    get_secret_value_response = secrets_client.get_secret_value(SecretId=openai_secret_key_arn)
    openai_secret_key = get_secret_value_response['SecretString']

    openai_client = OpenAI(
        api_key=openai_secret_key,
    )

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
        try:
            _lambda.invoke(
                FunctionName=os.environ['ACTION_HANDLER_FUNCTION_NAME'],
                Payload=json.dumps({"text": analysis_result}),
            )
        except Exception as e:
            print("Error invoking action handler function:", e)

    return {"statusCode": 200, "body": json.dumps({"message": "Success"})}