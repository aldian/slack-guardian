import json
import os
from importlib import reload
from unittest import mock

import boto3
import openai
import pytest


OPENAI_SECRET_ARN_1 = "OPENAI_SECRET_ARN_1"
OPENAI_SECRET_ARN_2 = "OPENAI_SECRET_ARN_2"
OPENAI_SECRET_ARN_3 = "OPENAI_SECRET_ARN_3"
OPENAI_SECRET_1 = "OPENAI_SECRET_1"
OPENAI_SECRET_2 = "OPENAI_SECRET_2"
OPENAI_SECRET_3 = "OPENAI_SECRET_3"
DYNAMODB_TABLE_1 = "table_1"
DYNAMODB_TABLE_2 = "table_2"
DYNAMODB_TABLE_3 = "table_3"
DYNAMODB_TABLE_4 = "table_4"
ACTION_HANDLER_1 = "action_handler_1"
ACTION_HANDLER_2 = "action_handler_2"


def dynamodb_table(table_name):
    table = mock.MagicMock()
    if table_name == DYNAMODB_TABLE_2:
        table.get_item.return_value = {"Item": {"MessageId": "message_id", "Timestamp": 123}}
    elif table_name == DYNAMODB_TABLE_3:
        table.get_item.side_effect = Exception("Get Item Exception")
    elif table_name == DYNAMODB_TABLE_4:
        table.put_item.side_effect = Exception("Put Item Exception")
    return table


def boto3_resource(resource_name):
    resource = mock.MagicMock()
    if resource_name == 'dynamodb':
        resource.Table.side_effect = dynamodb_table

    return resource

boto3.resource = mock.MagicMock()
boto3.resource.side_effect = boto3_resource


def secretsmanager_get_secret_value(SecretId):
    secret_string = ""
    if SecretId == OPENAI_SECRET_ARN_1:
        secret_string = OPENAI_SECRET_1
    elif SecretId == OPENAI_SECRET_ARN_2:
        secret_string = OPENAI_SECRET_2
    elif SecretId == OPENAI_SECRET_ARN_3:
        secret_string = OPENAI_SECRET_3

    secret_value = {
        "SecretString": secret_string
    }
    return secret_value


def lambda_invoke(FunctionName, InvocationType, Payload):
    result = mock.MagicMock()
    if FunctionName == ACTION_HANDLER_2:
        raise Exception("Invalid Function Name")

    return result


def boto3_client(service_name):
    client = mock.MagicMock()
    if service_name == 'secretsmanager':
        client.get_secret_value.side_effect = secretsmanager_get_secret_value
    elif service_name == 'lambda':
        client.invoke.side_effect = lambda_invoke

    return client


def openai_client(api_key):
    client = mock.MagicMock()
    completion = mock.MagicMock()
    analysis_result = "there is safety concern in the message."
    if api_key == OPENAI_SECRET_1:
        client.chat.completions.create.return_value = completion
    elif api_key == OPENAI_SECRET_3:
        client.chat.completions.create.return_value = completion
        analysis_result = "No safety concerns identified."
    else:
        client.chat.completions.create.side_effect = Exception("Invalid API Key")

    completion.choices[0].message.content = analysis_result
    return client

openai.OpenAI = mock.MagicMock()
openai.OpenAI.side_effect = openai_client


@pytest.fixture(autouse=True)
def run_before_and_after_tests(tmpdir):
    boto3.client = mock.MagicMock()
    boto3.client.side_effect = boto3_client

    yield


def test_success(): 
    os.environ['OPENAI_SECRET_KEY_ARN'] = OPENAI_SECRET_ARN_1
    os.environ['ANALYSIS_RESULTS_TABLE'] = DYNAMODB_TABLE_1
    os.environ['ACTION_HANDLER_FUNCTION_NAME'] = ACTION_HANDLER_1
    from lambdas import safety_analyzer
    safety_analyzer = reload(safety_analyzer)
    record = {
        "body": json.dumps({
            "text": "That child near the escalator is alone!",
        })
    }
    response = safety_analyzer.handler({"Records": [record]}, None)


def test_openai_completion_failed():
    os.environ['OPENAI_SECRET_KEY_ARN'] = OPENAI_SECRET_ARN_2
    os.environ['ANALYSIS_RESULTS_TABLE'] = DYNAMODB_TABLE_1
    os.environ['ACTION_HANDLER_FUNCTION_NAME'] = ACTION_HANDLER_1
    from lambdas import safety_analyzer
    safety_analyzer = reload(safety_analyzer)
    record = {
        "body": json.dumps({
            "text": "That child near the escalator is alone!",
        })
    }
    response = safety_analyzer.handler({"Records": [record]}, None)


def test_table_row_already_exists(): 
    os.environ['OPENAI_SECRET_KEY_ARN'] = OPENAI_SECRET_ARN_1
    os.environ['ANALYSIS_RESULTS_TABLE'] = DYNAMODB_TABLE_2
    from lambdas import safety_analyzer
    safety_analyzer = reload(safety_analyzer)
    record = {
        "body": json.dumps({
            "text": "That child near the escalator is alone!",
        })
    }
    response = safety_analyzer.handler({"Records": [record]}, None)


def test_table_get_item_exception():
    os.environ['OPENAI_SECRET_KEY_ARN'] = OPENAI_SECRET_ARN_1
    os.environ['ANALYSIS_RESULTS_TABLE'] = DYNAMODB_TABLE_3
    os.environ['ACTION_HANDLER_FUNCTION_NAME'] = ACTION_HANDLER_1
    from lambdas import safety_analyzer
    safety_analyzer = reload(safety_analyzer)
    record = {
        "body": json.dumps({
            "text": "That child near the escalator is alone!",
        })
    }
    response = safety_analyzer.handler({"Records": [record]}, None)


def test_table_put_item_exception():
    os.environ['OPENAI_SECRET_KEY_ARN'] = OPENAI_SECRET_ARN_1
    os.environ['ANALYSIS_RESULTS_TABLE'] = DYNAMODB_TABLE_4
    os.environ['ACTION_HANDLER_FUNCTION_NAME'] = ACTION_HANDLER_1
    from lambdas import safety_analyzer
    safety_analyzer = reload(safety_analyzer)
    record = {
        "body": json.dumps({
            "text": "That child near the escalator is alone!",
        })
    }
    response = safety_analyzer.handler({"Records": [record]}, None)


def test_no_safety_concern(): 
    os.environ['OPENAI_SECRET_KEY_ARN'] = OPENAI_SECRET_ARN_3
    os.environ['ANALYSIS_RESULTS_TABLE'] = DYNAMODB_TABLE_1
    os.environ['ACTION_HANDLER_FUNCTION_NAME'] = ACTION_HANDLER_1
    from lambdas import safety_analyzer
    safety_analyzer = reload(safety_analyzer)
    record = {
        "body": json.dumps({
            "text": "That child near the escalator is alone!",
        })
    }
    response = safety_analyzer.handler({"Records": [record]}, None)


def test_invalid_action_handler(): 
    os.environ['OPENAI_SECRET_KEY_ARN'] = OPENAI_SECRET_ARN_1
    os.environ['ANALYSIS_RESULTS_TABLE'] = DYNAMODB_TABLE_1
    os.environ['ACTION_HANDLER_FUNCTION_NAME'] = ACTION_HANDLER_2
    from lambdas import safety_analyzer
    safety_analyzer = reload(safety_analyzer)
    record = {
        "body": json.dumps({
            "text": "That child near the escalator is alone!",
        })
    }
    response = safety_analyzer.handler({"Records": [record]}, None)