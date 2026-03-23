import json
import os
from datetime import datetime, timezone
from urllib.parse import unquote_plus

import boto3

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["METADATA_TABLE"])
ENABLE_AI_TAGGING = os.environ.get("ENABLE_AI_TAGGING", "false").lower() == "true"
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "")


def _guess_content_type(key: str) -> str:
    key_lower = key.lower()
    if key_lower.endswith((".jpg", ".jpeg")):
        return "image/jpeg"
    if key_lower.endswith(".png"):
        return "image/png"
    if key_lower.endswith(".gif"):
        return "image/gif"
    if key_lower.endswith(".webp"):
        return "image/webp"
    if key_lower.endswith(".pdf"):
        return "application/pdf"
    if key_lower.endswith(".txt"):
        return "text/plain"
    if key_lower.endswith(".doc"):
        return "application/msword"
    if key_lower.endswith(".docx"):
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    if key_lower.endswith(".xls"):
        return "application/vnd.ms-excel"
    if key_lower.endswith(".xlsx"):
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return "application/octet-stream"


def _bedrock_stub(bucket: str, key: str) -> dict:
    # Starter hook for future integration.
    # Example extension:
    # bedrock = boto3.client("bedrock-runtime")
    # body = json.dumps({...})
    # response = bedrock.invoke_model(modelId=BEDROCK_MODEL_ID, body=body)
    # return parsed_response
    return {
        "ai_status": "not_enabled",
        "ai_summary": "Bedrock hook is scaffolded but disabled by default.",
    }


def lambda_handler(event, context):
    try:
        detail = event.get("detail", {})
        bucket = detail.get("bucket", {}).get("name")
        object_key = unquote_plus(detail.get("object", {}).get("key", ""))

        if not bucket or not object_key:
            return {"status": "ignored", "reason": "missing bucket or key"}

        head = s3.head_object(Bucket=bucket, Key=object_key)
        file_size = head.get("ContentLength", 0)
        content_type = head.get("ContentType") or _guess_content_type(object_key)
        etag = str(head.get("ETag", "")).replace('"', "")

        ai_payload = _bedrock_stub(bucket, object_key) if ENABLE_AI_TAGGING else {
            "ai_status": "disabled",
            "ai_summary": "AI enrichment disabled. Enable with environment variables.",
        }

        item = {
            "object_key": object_key,
            "bucket_name": bucket,
            "file_name": object_key.split("/")[-1],
            "file_size": file_size,
            "content_type": content_type,
            "etag": etag,
            "processed_at": datetime.now(timezone.utc).isoformat(),
            **ai_payload,
        }

        table.put_item(Item=item)

        return {"status": "processed", "object_key": object_key}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
