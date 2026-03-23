import json
import os
import re
import uuid
from urllib.parse import quote_plus

import boto3

s3 = boto3.client("s3")
BUCKET = os.environ["UPLOAD_BUCKET"]
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "*")
MAX_FILE_SIZE_MB = int(os.environ.get("MAX_FILE_SIZE_MB", "10"))

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


def _response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "OPTIONS,POST",
        },
        "body": json.dumps(body),
    }


def _safe_filename(file_name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._ -]", "_", file_name.strip())
    return quote_plus(cleaned or "upload.bin")


def lambda_handler(event, context):
    http_method = (
        event.get("requestContext", {}).get("http", {}).get("method")
        or event.get("httpMethod")
    )

    if http_method == "OPTIONS":
        return _response(200, {"message": "ok"})

    try:
        body = json.loads(event.get("body") or "{}")
        file_name = body.get("fileName")
        content_type = body.get("contentType")
        file_size = int(body.get("fileSize", 0) or 0)

        if not file_name or not content_type:
            return _response(400, {"error": "fileName and contentType are required"})

        if content_type not in ALLOWED_TYPES:
            return _response(400, {"error": f"Unsupported file type: {content_type}"})

        if file_size <= 0:
            return _response(400, {"error": "fileSize is required"})

        if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            return _response(400, {"error": f"File exceeds {MAX_FILE_SIZE_MB} MB limit"})

        safe_name = _safe_filename(file_name)
        key = f"uploads/{uuid.uuid4()}-{safe_name}"

        upload_url = s3.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": BUCKET,
                "Key": key,
                "ContentType": content_type,
            },
            ExpiresIn=300,
        )

        file_url = f"https://{BUCKET}.s3.amazonaws.com/{key}"

        return _response(
            200,
            {
                "uploadUrl": upload_url,
                "fileUrl": file_url,
                "key": key,
                "expiresIn": 300,
                "maxFileSizeMb": MAX_FILE_SIZE_MB,
            },
        )

    except ValueError:
        return _response(400, {"error": "Invalid fileSize value"})
    except Exception as exc:
        return _response(500, {"error": str(exc)})
