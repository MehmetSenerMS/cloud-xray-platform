import json
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key, Attr


TABLE_NAME = "XRayTransactions"
REGION_NAME = "us-east-1"
USER_PROFILE_SORT_KEY = "PROFILE"

dynamodb = boto3.resource("dynamodb", region_name=REGION_NAME)
table = dynamodb.Table(TABLE_NAME)


def convert_floats_to_decimal(data):
    return json.loads(
        json.dumps(data),
        parse_float=Decimal
    )


def convert_decimal_to_native(data):
    if isinstance(data, list):
        return [convert_decimal_to_native(item) for item in data]

    if isinstance(data, dict):
        return {
            key: convert_decimal_to_native(value)
            for key, value in data.items()
        }

    if isinstance(data, Decimal):
        if data % 1 == 0:
            return int(data)
        return float(data)

    return data


def save_item(item: dict):
    item = convert_floats_to_decimal(item)
    table.put_item(Item=item)
    return convert_decimal_to_native(item)


def save_user_profile(user_record: dict):
    user_record["record_type"] = "USER"
    user_record["transaction_id"] = USER_PROFILE_SORT_KEY

    return save_item(user_record)


def get_user_profile(user_id: str):
    response = table.get_item(
        Key={
            "user_id": user_id,
            "transaction_id": USER_PROFILE_SORT_KEY
        }
    )

    item = response.get("Item")

    if item is None:
        return None

    return convert_decimal_to_native(item)


def get_user_by_email(email: str):
    response = table.scan(
        FilterExpression=Attr("record_type").eq("USER") & Attr("email").eq(email)
    )

    items = response.get("Items", [])

    if not items:
        return None

    return convert_decimal_to_native(items[0])


def save_transaction_to_dynamodb(transaction_record: dict):
    transaction_record["record_type"] = "TRANSACTION"

    # DynamoDB item size limit nedeniyle image_base64 kaydetmiyoruz.
    transaction_record.pop("image_base64", None)

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

    return convert_decimal_to_native(transactions)

def get_transaction_by_id(user_id: str, transaction_id: str):
    response = table.get_item(
        Key={
            "user_id": user_id,
            "transaction_id": transaction_id
        }
    )

    item = response.get("Item")

    if item is None:
        return None

    return convert_decimal_to_native(item)