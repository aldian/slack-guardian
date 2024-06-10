import json


def handler(event, context):
    for record in event['Records']:
        message_body = json.loads(record['body'])
        print('rMessage body: {}'.format(json.dumps(message_body)))