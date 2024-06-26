import json
import os
from importlib import reload
from unittest import mock

import boto3
import pytest
import slack_sdk


SLACK_BOT_TOKEN_ARN_1 = "SLACK_BOT_TOKEN_ARN_1"
SLACK_BOT_TOKEN_ARN_2 = "SLACK_BOT_TOKEN_ARN_2"
SLACK_BOT_TOKEN_ARN_3 = "SLACK_BOT_TOKEN_ARN_3"
SLACK_BOT_TOKEN_ARN_4 = "SLACK_BOT_TOKEN_ARN_4"
SLACK_BOT_TOKEN_1 = "SLACK_BOT_TOKEN_1"
SLACK_BOT_TOKEN_2 = "SLACK_BOT_TOKEN_2"
SLACK_BOT_TOKEN_3 = "SLACK_BOT_TOKEN_3"
SLACK_BOT_TOKEN_4 = "SLACK_BOT_TOKEN_4"


def secretsmanager_get_secret_value(SecretId):
    secret_string = ""
    if SecretId == SLACK_BOT_TOKEN_ARN_1:
        secret_string = SLACK_BOT_TOKEN_1
    elif SecretId == SLACK_BOT_TOKEN_ARN_2:
        secret_string = SLACK_BOT_TOKEN_2
    elif SecretId == SLACK_BOT_TOKEN_ARN_3:
        secret_string = SLACK_BOT_TOKEN_3
    elif SecretId == SLACK_BOT_TOKEN_ARN_4:
        secret_string = SLACK_BOT_TOKEN_4

    secret_value = {
        "SecretString": secret_string
    }
    return secret_value


def boto3_client(service_name):
    client = mock.MagicMock()
    if service_name == 'secretsmanager':
        client.get_secret_value.side_effect = secretsmanager_get_secret_value

    return client


def slack_sdk_WebClient(token):
    slack_client = mock.MagicMock()
    if token == SLACK_BOT_TOKEN_1:
        slack_client.conversations_list.return_value = [
            {
                "channels": [
                    {
                        "name": "slack-guardian",
                        "id": "channel_id"
                    }
                ]
            }
        ]
    elif token == SLACK_BOT_TOKEN_2:
        slack_client.conversations_list.return_value = [
            {
                "channels": []
            }
        ]
    elif token == SLACK_BOT_TOKEN_3:
        slack_client.conversations_list.side_effect = slack_sdk.errors.SlackApiError("error", "response")
    elif token == SLACK_BOT_TOKEN_4:
        slack_client.conversations_list.return_value = [
            {
                "channels": [
                    {
                        "name": "slack-guardian",
                        "id": "channel_id"
                    }
                ]
            }
        ]
        slack_client.chat_postMessage.side_effect = slack_sdk.errors.SlackApiError("error", "response")


    return slack_client


@pytest.fixture(autouse=True)
def run_before_and_after_tests(tmpdir):
    boto3.client = mock.MagicMock()
    boto3.client.side_effect = boto3_client

    slack_sdk.WebClient = mock.MagicMock()
    slack_sdk.WebClient.side_effect = slack_sdk_WebClient

    yield


def test_success():
    os.environ['SLACK_BOT_TOKEN_ARN'] = SLACK_BOT_TOKEN_ARN_1
    from lambdas import slack_sender
    slack_sender = reload(slack_sender)

    slack_sender.handler({"Records": [
        {
            "body": json.dumps({"Message": json.dumps({"text": "Hello, World!"})}),
        }
    ]}, None)


def test_channel_not_found():
    os.environ['SLACK_BOT_TOKEN_ARN'] = SLACK_BOT_TOKEN_ARN_2
    from lambdas import slack_sender
    slack_sender = reload(slack_sender)

    slack_sender.handler({"Records": [
        {
            "body": json.dumps({"Message": json.dumps({"text": "Hello, World!"})}),
        }
    ]}, None)

def test_conversations_list_error():
    os.environ['SLACK_BOT_TOKEN_ARN'] = SLACK_BOT_TOKEN_ARN_3
    from lambdas import slack_sender
    slack_sender = reload(slack_sender)

    slack_sender.handler({"Records": [
        {
            "body": json.dumps({"Message": json.dumps({"text": "Hello, World!"})}),
        }
    ]}, None)


def test_post_message_error():
    os.environ['SLACK_BOT_TOKEN_ARN'] = SLACK_BOT_TOKEN_ARN_4
    from lambdas import slack_sender
    slack_sender = reload(slack_sender)

    slack_sender.handler({"Records": [
        {
            "body": json.dumps({"Message": json.dumps({"text": "Hello, World!"})}),
        }
    ]}, None)