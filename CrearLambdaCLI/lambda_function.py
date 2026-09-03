from urllib.parse import unquote_plus
import os
import boto3

s3 = boto3.client("s3")

PHOTO_EXTENSIONS = (".png", ".jpg", ".jpeg")
DEST_BUCKET = "output-for-a-lambda"


def lambda_handler(event, context):

    # Get bucket and file name from the S3 event
    bucket = event["Records"][0]["s3"]["bucket"]["name"]

    key = unquote_plus(
        event["Records"][0]["s3"]["object"]["key"]
    )

    print(f"Bucket: {bucket}")
    print(f"Key: {key}")

    # Get the filename and extension
    filename = os.path.basename(key)
    name, extension = os.path.splitext(filename)

    extension = extension.lower()

    print(f"Filename: {filename}")
    print(f"Name: {name}")
    print(f"Extension: {extension}")

    # Check if the file is a supported photo
    if extension not in PHOTO_EXTENSIONS:
        print(f"Unsupported file type: {extension}")

        return {
            "statusCode": 415,
            "body": "Unsupported Media Type"
        }

    # Download the image from S3
    response = s3.get_object(
        Bucket=bucket,
        Key=key
    )

    # Read the image bytes
    image_bytes = response["Body"].read()

    print(f"Image size: {len(image_bytes)} bytes")

    # Upload the image to the destination bucket
    s3.put_object(
        Bucket=DEST_BUCKET,
        Key=key,
        Body=image_bytes
    )

    print(f"Copied to: s3://{DEST_BUCKET}/{key}")

    return {
        "statusCode": 200,
        "body": "Photo copied successfully"
    }