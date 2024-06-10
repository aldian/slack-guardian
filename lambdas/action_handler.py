import json
import logging


def handler(event, context):
    logging.error('request: {} {}'.format(type(event), event))
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': 'Action Handler {}\n'.format(event)
    }