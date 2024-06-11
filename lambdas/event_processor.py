import json
import base64
import boto3
import os
from urllib.parse import parse_qs

from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler

# Initializes your app with your bot token and signing secret
#app = App(
#    token=os.environ.get("SLACK_BOT_TOKEN"),
#    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
#)
# arn:aws:secretsmanager:us-east-1:818954087576:secret:slack-signing-secret-eZYVYu
# arn:aws:secretsmanager:us-east-1:818954087576:secret:slack-bot-token-JHnfHB


def handler(event, context):
    secret_arn = os.environ['SLACK_SECRET_ARN']
    slack_signing_secret_arn = os.environ['SLACK_SIGNING_SECRET_ARN']
    slack_bot_token_arn = os.environ['SLACK_BOT_TOKEN_ARN']
    secrets_client = boto3.client("secretsmanager")

    get_secret_value_response = secrets_client.get_secret_value(SecretId=secret_arn)
    slack_verification_token = get_secret_value_response['SecretString']

    get_secret_value_response = secrets_client.get_secret_value(SecretId=slack_signing_secret_arn)
    slack_signing_secret = get_secret_value_response['SecretString']
    print("TOKEN 1:", slack_signing_secret)

    get_secret_value_response = secrets_client.get_secret_value(SecretId=slack_bot_token_arn)
    slack_bot_token = get_secret_value_response['SecretString']
    print("TOKEN 2:", slack_bot_token)

    # process_before_response must be True when running on FaaS
    app = App(
        process_before_response=True,
        token=slack_bot_token,
        signing_secret=slack_signing_secret,
    )

    slack_handler = SlackRequestHandler(app=app)

    # Verification
    body = event["body"]
    if event.get("isBase64Encoded"):  # Handle base64 encoded body
        body = base64.b64decode(body)
    body = json.loads(body)

    token = body.get("token", None)
    if token != slack_verification_token:
        return {"statusCode": 401, "body": f"Unauthorized: {token} != {slack_verification_token}"}  # Stop unauthorized requests

    # Process the event
    slack_event = body.get("event")
    if not slack_event:
        return {"statusCode": 400, "body": "Invalid request"}

    queue_url = os.environ['SLACK_EVENT_QUEUE_URL']
    sqs = boto3.client('sqs')

    # Send to SQS for further processing
    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(slack_event)
    )

    # Respond to Slack to acknowledge the event
    # return {"statusCode": 200, "body": "OK"}
    resp = slack_handler.handle(event, context)
    print("RESP:", resp)
    return resp