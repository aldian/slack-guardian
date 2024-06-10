import json
import logging


def handler(event, context):
    logging.error(f"Received event: {event}")
    for record in event['Records']:
        message_body = json.loads(record['body'])

        # Log the message body
        logging.error(f"Received message: {message_body}")  # Use f-string for better formatting

        # Perform safety analysis on the message_body
        # ...

        # Take actions based on the analysis
        # ...