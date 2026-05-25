import json
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key


TABLE_NAME = "XRayTransactions"
REGION_NAME = "us-east-1"

USER_PROFILE_SORT_KEY = "PROFILE"


dynamodb = boto3.resource(
    "dynamodb",
    region_name=REGION_NAME
)

table = dynamodb.Table(TABLE_NAME)


def convert_floats_to_decimal(data):
    return json.loads(
        json.dumps(data),
        parse_float=Decimal
    )


def save_item(item: dict):
    item = convert_floats_to_decimal(item)
    table.put_item(Item=item)
    return item


def save_user_profile(user_record: dict):
    return save_item(user_record)


def get_user_profile(user_id: str):
    response = table.get_item(
        Key={
            "user_id": user_id,
            "transaction_id": USER_PROFILE_SORT_KEY
        }
    )

    return response.get("Item")


def get_user_by_email(email: str):
    response = table.scan(
        FilterExpression=Key("record_type").eq("USER") & Key("email").eq(email)
    )

    items = response.get("Items", [])

    if not items:
        return None

    return items[0]


def save_transaction_to_dynamodb(transaction_record: dict):
    transaction_record["record_type"] = "TRANSACTION"
    return save_item(transaction_record)


def get_transactions_by_user(user_id: str):
    response = table.query(
        KeyConditionExpression=Key("user_id").eq(user_id)
    )

    items = response.get("Items", [])

    transactions = [
        item for item in items
        if item.get("record_type") == "TRANSACTION"
    ]

    return transactions