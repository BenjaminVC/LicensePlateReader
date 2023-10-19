import boto3
import xml.etree.ElementTree as ET
import io
import os
import sys


# uploads valid xml or json file to DMV S3 bucket with tag
def upload_to_s3(s3_client, bucket, file_path, tag1, tag2, tag3):
    print("Uploading to CA DMV...")
    try:
        # extract filename from file_path and upload file to S3
        file_name = os.path.basename(file_path)
        s3_client.upload_file(file_path, bucket, file_name)
        print("Uploading file...")

        # create waiter...
        waiter = s3_client.get_waiter('object_exists')
        # wait for upload to 'exist' before adding tag
        waiter.wait(Bucket=bucket, Key=file_name)

        # add tags to the uploaded file
        s3_client.put_object_tagging(
            Bucket=bucket,
            Key=file_name,
            Tagging={
                'TagSet': [
                    {
                        'Key': 'Location',
                        'Value': tag1
                    },
                    {
                        'Key': 'DateTime',
                        'Value': tag2
                    },
                    {
                        'Key': 'Type',
                        'Value': tag3
                    },
                ]
            }
        )
        print(f"Tagged {file_name}, with location '{tag1}', "
              f"DateTime '{tag2}', and Type {tag3}")
        return True

    except Exception as e:
        print("Upload to CA DMV failed.")
        print(e)
        return False


# checks if passed file exists, returns boolean
def check_dir(file_path):
    has_files = False

    # check for non-empty directory of vaccination data
    vaccine_data = file_path
    if not os.path.exists(vaccine_data):
        print("Could not find:", vaccine_data, "nothing to upload to CDC.")
    else:
        has_files = True
        print(vaccine_data, "has records to upload to CDC.")
    return has_files


# checks that the user passed two arguments
def has_args():
    num_args = len(sys.argv)
    if num_args == 5:
        print("Valid # of arguments passed to UploadData.py")
        return True
    else:
        print("User did not pass a valid # of arguments to UploadData.py")
        return False


# UploadData script start
if __name__ == '__main__':
    # initial setup vars
    can_upload = False

    # cli args
    valid_init = has_args()
    path_to_data = sys.argv[1]
    tag_arg1 = sys.argv[2]
    tag_arg2 = sys.argv[3]
    tag_arg3 = sys.argv[4]

    # check user passed file and that the tag_arg matches the file extension
    site_has_data = check_dir(path_to_data)

    # check conditions before creating aws client
    if site_has_data and valid_init:
        can_upload = True
    else:
        print("Could not validate", path_to_data)
        exit(2)

    if can_upload:
        print("Ready to upload:", path_to_data)
        # boto3 s3 resource using default .aws credentials
        s3 = boto3.client('s3')
        bucket_name = 'dmv-ticketing'
        if upload_to_s3(s3, bucket_name, path_to_data, tag_arg1, tag_arg2, tag_arg3):
            print("Uploaded to", bucket_name)
        else:
            print("File could not be uploaded to", bucket_name)

exit(0)
