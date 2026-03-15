import json
import boto3

s3 = boto3.client("s3")
BUCKET_NAME = "felicity2025"

def lambda_handler(event, context):
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)
    
    if "Contents" in response:
        images = [
            obj['Key']
            for obj in response["Contents"]
            if obj['Key'].lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))
        ]
    else:
        images = []
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(images)
    }

