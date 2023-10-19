import json
import boto3
import re
from urllib.parse import unquote_plus

# this Lambda is listening to PUT events on the DMV bucket and...
# extracts the S3 file content of XML files validated by UploadData.py only.
# This Lambda puts a JSON message in the DownwardQueue with the...
# plate # it reads from the XML
print("imports done")

# S3, Rekognition, and SQS clients setup
rekog = boto3.client('rekognition')
sqs = boto3.client('sqs')
s3_client = boto3.client('s3', region_name='')
eventbridge = boto3.client('events')


def lambda_handler(event, context):
    is_ca_plate = False
    print(context.aws_request_id)

    # get the name of the bucket that triggered the event
    bucket_name = event['Records'][0]['s3']['bucket']['name']

    if bucket_name != 'dmv-ticketing':
        print("Lambda triggered by incorrect bucket.  Check AWS Lambda console configuration.")
        return

    # get the file key and decode the special characters using unquote_plus pkg
    key = unquote_plus(event['Records'][0]['s3']['object']['key'])

    # store the object and decode it's content
    obj = s3_client.get_object(Bucket=bucket_name, Key=key)

    # store the object's tag
    tags = s3_client.get_object_tagging(Bucket=bucket_name, Key=key)

    # create a request to Rekognition for text detection
    response = rekog.detect_text(
        Image={
            'S3Object': {
                'Bucket': bucket_name,
                'Name': key
            }
        }
    )

    # list to hold all detected text
    detected_texts = []
    # re pattern matches a typical CA license plate
    pattern = re.compile(r'\d[A-Za-z]{3}\d{3}')
    # store and iterate through TextDetections elements
    text_detections = response['TextDetections']
    for text in text_detections:
        detected_text = text['DetectedText']
        detected_texts.append(detected_text)
        if pattern.match(detected_text):
            ticketed_plate = str(detected_text)
        print(detected_text)
        if detected_text.lower() == 'california':
            is_ca_plate = True
            print("found cali plate!")

    # send the plate number as a JSON message to the downward queue
    if is_ca_plate:
        response = sqs.send_message(QueueUrl='https://sqs.us-west-2.amazonaws.com/286336465435/cdc-downward',
                                    MessageBody=json.dumps({'plate': ticketed_plate, 'tags': tags}))
    # send the details of the non-CA plate to AWS EventBridge
    else:
        print("found non-cali plate!")
        response = eventbridge.put_events(
            Entries=[
                {
                    'Source': 'dmv-ticketing',
                    'DetailType': 'non-ca-plate-detected',
                    'Detail': json.dumps({'detected-texts': detected_text, 'tags': tags}),
                    'EventBusName': 'default'
                }
            ]
        )

    print(response)
