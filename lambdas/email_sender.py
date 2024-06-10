import json


def handler(event, context):
    for i, record in enumerate(event['Records']):
        message_body = json.loads(record['body'])
        print('{:2d}. Message body: {}'.format(i + 1, json.dumps(message_body)))