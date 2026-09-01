import json
from urllib.parse import unquote_plus
import boto3

s3 = boto3.client("s3")

DEST_BUCKET = "output-photos-bucket-asl"
def lambda_handler(event, context):
    # Get bucket and file name from the S3 event
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = unquote_plus(
        event["Records"][0]["s3"]["object"]["key"]
    )

    print(f"Bucket: {bucket}")
    print(f"File: {key}")

    # Download the image from S3
    response = s3.get_object(
        Bucket=bucket,
        Key=key
    )

    # Actual image bytes
    image_bytes = response["Body"].read()

    print(f"Image size: {len(image_bytes)} bytes")
    image_bytes = response["Body"].read()

    # Upload it to the other bucket
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