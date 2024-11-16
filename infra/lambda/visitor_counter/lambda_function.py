import json
import urllib
import boto3
import os
from botocore.exceptions import ClientError
from aws_lambda_powertools import Logger
from datetime import datetime

dynamodb_resource = boto3.resource("dynamodb", region_name="eu-west-1")
table = dynamodb_resource.Table(os.environ["TABLE"])

def add_visitor_to_table(current_date: str, current_hour: str) -> None:
    visitor_count = 1

    update_attributes = {
        "date": current_date,
        "hour": current_hour,
        "visitors": visitor_count,
    }

    return None


def get_visitor_count():
    pass


def lambda_handler(event, context):
    logger.info(event)

    if "resource" in event and "/add_visitor" in event:
        try:
            current_time = datetime.now()
            current_date = current_time.strftime("%Y-%m-%d")
            current_hour = current_time.strftime("%H")

            add_visitor_to_table(current_date=current_date, current_hour=current_hour)

        except Exception as e:
            return {
                'statusCode': 500,
                'body': f"Error updating visitor count: {str(e)}"
            }
        
    elif "resource" in event and "/get_visitor_count" in event:
        get_visitor_count()

    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
