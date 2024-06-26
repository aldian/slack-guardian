import base64
import os
import json
from importlib import reload
from unittest import mock

import boto3
import pytest
import slack_bolt

os.environ['SLACK_SIGNING_SECRET_ARN'] = 'TESTING-ARN'
os.environ['SLACK_BOT_TOKEN_ARN'] = 'TESTING-ARN'
os.environ['SLACK_EVENT_QUEUE_URL'] = 'https://event-queue-url'

def boto3_client(service_name):
    client = mock.MagicMock()
    if service_name == 'secretsmanager':
        client.get_secret_value.return_value = {"SecretString": "SECRET"}

    return client


slack_bolt.App = mock.MagicMock()


@pytest.fixture(autouse=True)
def run_before_and_after_tests(tmpdir):
    boto3.client = mock.MagicMock()
    boto3.client.side_effect = boto3_client

    yield


def test_ignore_non_user_message(): 
    from lambdas import event_processor
    event_processor = reload(event_processor)
    body = {
        "event": {
            "bot_id": "bot_id",
            "subtype": "subtype"
        }
    }
    response = event_processor.handler({
        "body": base64.b64encode(json.dumps(body).encode()).decode(),
        "isBase64Encoded": True,
    }, None)


def test_not_a_slack_event():
    from lambdas import event_processor
    event_processor = reload(event_processor)
    body = {
        "hello": "world",
    }
    response = event_processor.handler({"body": json.dumps(body)}, None)



def test_user_message(): 
    from lambdas import event_processor
    event_processor = reload(event_processor)
    body = {
        "event": {
            "type": "message",
        }
    }
    response = event_processor.handler({
        "body": json.dumps(body),
    }, None)