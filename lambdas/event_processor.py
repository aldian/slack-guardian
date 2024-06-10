import json
import base64
import boto3
import logging
import os
from urllib.parse import parse_qs


def handler(event, context):
    secret_arn = os.environ['SLACK_SECRET_ARN']
    secrets_client = boto3.client("secretsmanager")
    get_secret_value_response = secrets_client.get_secret_value(SecretId=secret_arn)
    slack_verification_token = get_secret_value_response['SecretString']

    # Verification
    body = event["body"]
    logging.error(f"BODY ORIGINAL: {body}")
    if event.get("isBase64Encoded"):  # Handle base64 encoded body
        body = base64.b64decode(body)
    logging.error(f"BODY DECODED: {body}")
    body = parse_qs(body)
    logging.debug(f"BODY PARSED: {body}")

    token = body.get("token", [None])[0]
    if token != slack_verification_token:
        return {"statusCode": 401, "body": f"Unauthorized: {token} != {slack_verification_token}"}  # Stop unauthorized requests

    # Process the event
    slack_event = json.loads(body.get("payload", ["{}"])[0])
    event_type = slack_event.get("type")

    if event_type == "url_verification":
        # Respond to the initial Slack challenge
        return {"statusCode": 200, "body": slack_event.get("challenge")}

    elif event_type == "event_callback":
        event_subtype = slack_event["event"]["type"]

        if event_subtype == "app_mention":
            QUEUE_URL = os.environ['SLACK_EVENT_QUEUE_URL']
            sqs = boto3.client('sqs')

            # Send to SQS for further processing
            sqs.send_message(
                QueueUrl=QUEUE_URL,
                MessageBody=json.dumps(slack_event)
            )

            # Respond to Slack to acknowledge the event
            return {"statusCode": 200, "body": "OK"}
        else:
            return {"statusCode": 200, "body": "Unsupported event"}  # Handle other event types if needed

    else:
        return {"statusCode": 400, "body": "Invalid request"}