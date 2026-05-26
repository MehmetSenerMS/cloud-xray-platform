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


def generate_presigned_image_url(
    image_s3_key: str,
    expires_in: int = 600
) -> str:
    return s3_client.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": S3_BUCKET,
            "Key": image_s3_key
        },
        ExpiresIn=expires_in
    )

def delete_image_from_s3(image_s3_key: str):
    s3_client.delete_object(
        Bucket=S3_BUCKET,
        Key=image_s3_key
    )

    return {
        "deleted": True,
        "image_s3_key": image_s3_key
    }