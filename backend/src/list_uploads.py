import json
import os
from decimal import Decimal

import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["METADATA_TABLE"])
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "*")


def _json_default(value):
    if isinstance(value, Decimal):
        return float(value)
    raise TypeError


def _response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "OPTIONS,GET",
        },
        "body": json.dumps(body, default=_json_default),
    }


def lambda_handler(event, context):
    http_method = (
        event.get("requestContext", {}).get("http", {}).get("method")
        or event.get("httpMethod")
    )

    if http_method == "OPTIONS":
        return _response(200, {"message": "ok"})

    try:
        response = table.scan(Limit=100)
        items = response.get("Items", [])
        items.sort(key=lambda item: item.get("processed_at", ""), reverse=True)
        return _response(200, {"items": items})
    except Exception as exc:
        return _response(500, {"error": str(exc)})
