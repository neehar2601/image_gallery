#lambda function

import boto3
import os
import json

s3 = boto3.client('s3')
BUCKET_NAME = os.environ['BUCKET_NAME']  # set via environment variable

def lambda_handler(event, context):
    # Get date from query string
    date = event.get('queryStringParameters', {}).get('date', '')
    prefix = f"images/{date}/" if date else "images/"

    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
        if 'Contents' not in response:
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"images": []})
            }

        image_urls = [
            f"https://{BUCKET_NAME}.s3.amazonaws.com/{obj['Key']}"
            for obj in response['Contents']
            if not obj['Key'].endswith('/')
        ]

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"images": image_urls})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
