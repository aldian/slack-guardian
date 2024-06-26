import os
from unittest import mock

import boto3
import pytest



os.environ['SAFETY_ALERTS_TOPIC_ARN'] = 'TESTING-ARN'


def boto3_client(service_name):
    client = mock.MagicMock()
    return client


@pytest.fixture(autouse=True)
def run_before_and_after_tests(tmpdir):
    boto3.client = mock.MagicMock()
    boto3.client.side_effect = boto3_client

    yield


from lambdas import action_handler


def test_success():
    action_handler.handler({}, None)


def test_invalid_data():
    action_handler.handler(set(), None)