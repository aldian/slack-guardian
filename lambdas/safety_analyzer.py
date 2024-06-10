import json
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Set the desired logging level (INFO, DEBUG, etc.)


def handler(event, context):
    for record in event['Records']:
        message_body = json.loads(record['body'])

        # Log the message body
        logger.info(f"Received message: {message_body}")  # Use f-string for better formatting

        # Perform safety analysis on the message_body
        # ...

        # Take actions based on the analysis
        # ...