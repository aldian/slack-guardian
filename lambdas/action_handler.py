import json
import logging
import os

import boto3


def handler(event, context):
    logging.error('request: {} {}'.format(type(event), event))

    sns_client = boto3.client('sns')
    topic_arn = os.environ['SAFETY_ALERTS_TOPIC_ARN']

    try:
        sns_client.publish(
            TopicArn=topic_arn,
            Message=json.dumps(event),  # Assuming 'message' is a dictionary you want to publish
            Subject='SlackGuardian Safety Alert'  # Optional subject line
        )
    except Exception as e:
        logging.error(f"Error publishing to SNS: {e}")

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': 'Action Handler {}\n'.format(event)
    }