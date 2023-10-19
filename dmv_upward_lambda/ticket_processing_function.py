import json
import boto3
from botocore.exceptions import ClientError

print("imports done")

# SQS and SES client set up
sqs_client = boto3.client('sqs')
ses_client = boto3.client('ses')

# ticket amount dict
ticket_amounts = {
    'no_stop': '$300.00',
    'no_full_stop_on_right': '$75.00',
    'no_right_on_red': '$125.00'
}


def lambda_handler(event, context):
    print(context.aws_request_id)

    # read the message from the downward queue that triggered the event
    for record in event['Records']:
        message = json.loads(record['body'])

        # extract vehicle information and tags
        vehicle_info = message['Vehicle']
        tags = message['Tags']

        # Initialize variables
        violation_type = None
        violation_date = None
        violation_location = None

        # Loop through 'TagSet' and assign values based on 'Key'
        for tag in tags['TagSet']:
            if tag['Key'] == 'Type':
                violation_type = tag['Value']
            elif tag['Key'] == 'DateTime':
                violation_date = tag['Value']
            elif tag['Key'] == 'Location':
                violation_location = tag['Value']

        if violation_type is None or violation_date is None or violation_location is None:
            print("Missing necessary tag information.")
            # decide on the course of action: return, raise an error, etc.
            continue

        # check violation type from tags and use ticket amount dict to set amount
        ticket_amount = ticket_amounts.get(violation_type, 'Invalid violation type')

        # Email details
        SENDER = "<ben@benvancise.com>"
        RECIPIENT = vehicle_info['ContactEmail']  # contact email from vehicle_info
        AWS_REGION = "us-west-2"
        SUBJECT = "Traffic Violation Ticket Details"

        BODY_TEXT = f"""Your vehicle was involved in a traffic violation. Please pay the specified ticket amount within 30 days:
        Vehicle: {vehicle_info['Color']} {vehicle_info['Make']} {vehicle_info['Model']}
        License plate: {vehicle_info['PlateNumber']}
        Date: {violation_date}
        Violation address: {violation_location}
        Violation type: {violation_type}
        Ticket amount: {ticket_amount}
        """

        CHARSET = "UTF-8"

        # Try to send the email.
        try:
            # Provide the contents of the email.
            response = ses_client.send_email(
                Destination={
                    'ToAddresses': [
                        RECIPIENT,
                    ],
                },
                Message={
                    'Body': {
                        'Text': {
                            'Charset': CHARSET,
                            'Data': BODY_TEXT,
                        },
                    },
                    'Subject': {
                        'Charset': CHARSET,
                        'Data': SUBJECT,
                    },
                },
                Source=SENDER,
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print("Email sent! Message ID:", response['MessageId'])
