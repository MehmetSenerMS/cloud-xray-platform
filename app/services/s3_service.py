import base64
import boto3


S3_BUCKET = "cloud-xray-images-msmes"
REGION_NAME = "us-east-1"

s3_client = boto3.client(
    "s3",
    region_name=REGION_NAME
)


def upload_image_to_s3(
    base64_image: str,
    user_id: str,
    transaction_id: str
) -> str:
    image_data = base64.b64decode(base64_image)

    image_s3_key = f"xray-images/{user_id}/{transaction_id}.png"

    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=image_s3_key,
        Body=image_data,
        ContentType="image/png"
    )

    return image_s3_key