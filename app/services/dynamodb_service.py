import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal
import json

TABLE_NAME = "XRayTransactions"
REGION_NAME = "us-east-1"

dynamodb = boto3.resource(
    "dynamodb",
    region_name=REGION_NAME
)

table = dynamodb.Table(TABLE_NAME)


def save_transaction_to_dynamodb(transaction_record: dict):

    transaction_record = json.loads(
        json.dumps(transaction_record),
        parse_float=Decimal
    )

    table.put_item(Item=transaction_record)

    return transaction_record

def get_transactions_by_user(user_id: str):
    response = table.query(
        KeyConditionExpression=Key("user_id").eq(user_id)
    )

    return response.get("Items", [])