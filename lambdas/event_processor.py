import json
import base64
import boto3
import os

from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler


slack_signing_secret_arn = os.environ['SLACK_SIGNING_SECRET_ARN']
slack_bot_token_arn = os.environ['SLACK_BOT_TOKEN_ARN']
secrets_client = boto3.client("secretsmanager")

get_secret_value_response = secrets_client.get_secret_value(SecretId=slack_signing_secret_arn)
slack_signing_secret = get_secret_value_response['SecretString']

get_secret_value_response = secrets_client.get_secret_value(SecretId=slack_bot_token_arn)
slack_bot_token = get_secret_value_response['SecretString']

app = App(
    process_before_response=True,
    token=slack_bot_token,
    signing_secret=slack_signing_secret,
)

queue_url = os.environ['SLACK_EVENT_QUEUE_URL']
sqs = boto3.client('sqs')


def handler(event, context):

    slack_handler = SlackRequestHandler(app=app)

    body = event["body"]
    if event.get("isBase64Encoded"):
        body = base64.b64decode(body)
    body = json.loads(body)
    print("BODY:", body)

    slack_event = body.get("event")
    if not slack_event:
        return slack_handler.handle(event, context)

    if slack_event.get("bot_id") or slack_event.get("subtype"):
        # Ignore messages from bots or subtype
        return slack_handler.handle(event, context)
    
    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(slack_event)
    )

    return slack_handler.handle(event, context)