import boto3
import xml.etree.ElementTree as ET
import time
import json
from datetime import datetime

# set up clients for SQS polling and messaging
sqs_client = boto3.client('sqs')
QUEUE_URL_DOWNWARD = ''
QUEUE_URL_UPWARD = ''

# load insurance database
tree = ET.parse('DMVDatabase.xml')


# fetch DMV data based on the plate number consumed from the downward queue
def fetch_dmv_data(plate_num):
    for vehicle in tree.findall('vehicle'):
        # check that the plate number matches
        if vehicle.get('plate') == plate_num:
            owner = vehicle.find('owner')

            dmv_data = {
                'Make': vehicle.find('make').text,

                'Model': vehicle.find('model').text,
                'Color': vehicle.find('color').text,
                'Owner': owner.find('name').text,
                'ContactEmail': owner.find('contact').text
            }
            print(f'Vehicle Data: {dmv_data}')  # log vehicle data to console
            return dmv_data
    return None


# daemon thread that keeps running
while True:
    # uses long polling to retrieve messages, i.e. anything > 0 seconds, maximum 20 seconds
    response = sqs_client.receive_message(
        QueueUrl=QUEUE_URL_DOWNWARD,
        WaitTimeSeconds=5
    )

    # message is received
    if 'Messages' in response:
        for message in response['Messages']:
            receipt_handle = message['ReceiptHandle']

            # get the current plate number from the queue
            message_body = json.loads(message['Body'])
            plate_num = message_body['plate']
            tags = message_body['tags']

            # log the message with some additional timestamp info to the console
            print(f"Date: {datetime.now().isoformat()} Read message: {message['Body']}")

            # fetch DMV data from DMVDatabase and set the response message accordingly
            dmv_data = fetch_dmv_data(plate_num)
            if dmv_data:
                response_message = {
                    'Vehicle': {
                        'PlateNumber': plate_num,
                        'Make': dmv_data['Make'],
                        'Model': dmv_data['Model'],
                        'Color': dmv_data['Color'],
                        'Owner': dmv_data['Owner'],
                        'ContactEmail': dmv_data['ContactEmail']
                    },
                    'Tags': tags
                }
            else:
                response_message = {
                    'Message': f"Vehicle with Plate {plate_num} does not exist in DMV Database",
                    'Tags': tags
                }

            # send message to SQS
            sqs_client.send_message(
                QueueUrl=QUEUE_URL_UPWARD,
                MessageBody=json.dumps(response_message)
            )

            # log the response message and additional timestamp info to console
            print(f"Date: {datetime.now().isoformat()} Posted message: {response_message}")

            # delete the message from the downward queue, indicating that the message was consumed
            sqs_client.delete_message(
                QueueUrl=QUEUE_URL_DOWNWARD,
                ReceiptHandle=receipt_handle
            )

    # sleep for one second before polling SQS again
    time.sleep(1)
