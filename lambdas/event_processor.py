import json
import base64
import boto3
import os
from urllib.parse import parse_qs


def handler(event, context):
    secret_arn = os.environ['SLACK_SECRET_ARN']
    secrets_client = boto3.client("secretsmanager")
    get_secret_value_response = secrets_client.get_secret_value(SecretId=secret_arn)
    slack_verification_token = get_secret_value_response['SecretString']

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
    return {"statusCode": 200, "body": "OK"}