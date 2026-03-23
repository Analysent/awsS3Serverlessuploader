import json
import os
import uuid
import boto3

s3 = boto3.client("s3")
BUCKET = os.environ["UPLOAD_BUCKET"]

ALLOWED_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "application/pdf",
    "text/plain",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
}


def response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "OPTIONS,POST",
        },
        "body": json.dumps(body),
    }


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
        file_name = body.get("fileName")
        content_type = body.get("contentType")

        if not file_name or not content_type:
            return response(400, {"error": "Missing fileName or contentType"})

        if content_type not in ALLOWED_TYPES:
            return response(400, {"error": "Unsupported file type"})

        key = f"uploads/{uuid.uuid4()}-{file_name}"

        url = s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": BUCKET,
                "Key": key,
                "ContentType": content_type,
            },
            ExpiresIn=300,
        )

        return response(200, {
            "uploadUrl": url,
            "fileKey": key
        })

    except Exception as e:
        return response(500, {"error": str(e)})
