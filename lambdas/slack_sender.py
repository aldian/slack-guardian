import json
import logging
import os

import boto3
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


slack_bot_token_arn = os.environ['SLACK_BOT_TOKEN_ARN']
secrets_client = boto3.client("secretsmanager")

get_secret_value_response = secrets_client.get_secret_value(SecretId=slack_bot_token_arn)
slack_bot_token = get_secret_value_response['SecretString']


def handler(event, context):
    slack_client = WebClient(token=slack_bot_token)

    channel_id = None
    try:
        # Call the conversations.list method using the WebClient
        # help(client.conversations_list)
        for result in slack_client.conversations_list(types=['public_channel', 'private_channel']):
            for channel in result["channels"]:
                if channel['name'] == 'slack-guardian':
                    channel_id = channel['id']
                    break
            if channel_id:
                break
        else:
            logging.error("Channel not found")
            return
    except SlackApiError as e:
        logging.error(f"{e}")
        return

    for i, record in enumerate(event['Records']):
        body = json.loads(record['body'])
        message = json.loads(body['Message'])
        print('{:2d}. Message body: {}'.format(i + 1 ,message))

        try:
            result = slack_client.chat_postMessage(
                channel=channel['id'],
                text=message["text"],
            )
        except Exception as e:
            logging.error(f"{e}")
            continue