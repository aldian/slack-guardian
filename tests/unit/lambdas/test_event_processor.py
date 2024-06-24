import os
from unittest import mock

import boto3
import slack_bolt

os.environ['SLACK_SIGNING_SECRET_ARN'] = 'TESTING-ARN'
os.environ['SLACK_BOT_TOKEN_ARN'] = 'TESTING-ARN'
os.environ['SLACK_EVENT_QUEUE_URL'] = 'https://event-queue-url'

def boto3_client(service_name):
    client = mock.MagicMock()
    if service_name == 'secretsmanager':
        client.get_secret_value.return_value = {"SecretString": "SECRET"}

    return client

boto3.client = mock.MagicMock()
boto3.client.side_effect = boto3_client

slack_bolt.App = mock.MagicMock()

from lambdas import event_processor
#from slack_guardian.lambdas.event_processor import handler


def test_handler():
    pass