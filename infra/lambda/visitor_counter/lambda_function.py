import json
import urllib
import boto3
import os
from botocore.exceptions import ClientError
from aws_lambda_powertools import Logger
from datetime import datetime

# Initialize logger
logger = Logger()

dynamodb_resource = boto3.resource("dynamodb", region_name="eu-west-1")
TABLE = dynamodb_resource.Table(os.environ["TABLE"])

def add_visitor_to_table(current_date: str) -> str:
    updates = [
        # Daily counter
        {
            "Key": {"pk": "daily", "sk": current_date},
            "UpdateExpression": "ADD visitors :inc",
            "ExpressionAttributeValues": {":inc": 1}
        },
        # Total counter
        {
            "Key": {"pk": "total", "sk": "historic"},
            "UpdateExpression": "ADD visitors :inc",
            "ExpressionAttributeValues": {":inc": 1}
        }
    ]
    
    for update in updates:
        TABLE.update_item(**update)
    
    logger.info(">>> Visitor added to table.")

    return {
        "statusCode": 200,
        "headers": headers,
        "body": json.dumps({
            "message": ">>> Visitor added to table."
        })
    }


def get_visitor_count(pk: str, sk: str) -> int | None:
    try:
        response = TABLE.get_item(
            Key={
                "pk": pk,
                "sk": sk
            }
        )
        logger.info(response)
        
        item = response.get("Item", {})
        visitors = item.get("visitors", 0) 

        logger.info(">>> Visitors retrieved.")
        logger.info(visitors)

        return visitors
    
    except Exception as e:
        logger.info(str(e))

        return None


def lambda_handler(event, context):
    logger.info(event)

    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
    }

    current_time = datetime.now()
    current_date = current_time.strftime("%Y-%m-%d")

    if "resource" in event and "add_visitor" in event["resource"]:
        try:
            return add_visitor_to_table(current_date=current_date)

        except Exception as e:
            logger.info(str(e))

            return {
                "statusCode": 500,
                "headers": headers,
                "body": json.dumps({
                    "message": str(e)
                })
            }
        
    elif "resource" in event and "/get_visitor_count" in event["resource"]:
        try:
            total_visitors = int(get_visitor_count(pk="total", sk="historic"))
            daily_visitors = int(get_visitor_count(pk="daily", sk=current_date))

            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({
                    "total_visitors": total_visitors,
                    "daily_visitors": daily_visitors
                })
            }

        except Exception as e:
            logger.info(str(e))

            return {
                "statusCode": 500,
                "headers": headers,
                "body": json.dumps({
                    "message": str(e)
                })
            }

    logger.info("Invalid endpoint.")

    return {
        "statusCode": 400,
        "headers": headers,
        "body": json.dumps({
            "message": "Invalid endpoint"
        })
    }
