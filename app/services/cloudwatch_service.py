import boto3


REGION_NAME = "us-east-1"
NAMESPACE = "CloudXRayPlatform"

cloudwatch_client = boto3.client(
    "cloudwatch",
    region_name=REGION_NAME
)


def put_metric(
    metric_name: str,
    value: float,
    unit: str = "Seconds"
):
    cloudwatch_client.put_metric_data(
        Namespace=NAMESPACE,
        MetricData=[
            {
                "MetricName": metric_name,
                "Value": value,
                "Unit": unit
            }
        ]
    )