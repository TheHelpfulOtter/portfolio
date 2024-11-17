import json
import urllib
import boto3
import os
from botocore.exceptions import ClientError
from aws_lambda_powertools import Logger
from datetime import datetime

dynamodb_resource = boto3.resource("dynamodb", region_name="eu-west-1")
TABLE = dynamodb_resource.Table(os.environ["TABLE"])

def add_visitor_to_table(current_date: str) -> None:
    try:
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
        
        logger.info(">>> DDB Table updated.")

        return None
        
    except Exception as e:
        logger.info(str(e))

        return None


def get_visitor_count(pk: str, sk: str) -> int | None:
    try:
        response = TABLE.get_item(
            Key={
                "pk": pk,
                "sk": sk
            }
        )
        
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
        "Access-Control-Allow-Origin": "*",  # Or your specific domain
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
    }

    current_time = datetime.now()
    current_date = current_time.strftime("%Y-%m-%d")

    if "resource" in event and "add_visitor" in event["resource"]:
        try:
            add_visitor_to_table(current_date=current_date)

            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({
                    "message": "Added visitors."
                })
            }

        except Exception as e:
            logger.info(str(e))

            return {
                "statusCode": 500,
                "headers": headers,
                "body": json.dumps({
                    "message": "Could not add visitor to table."
                })
            }
        
    elif "resource" in event and "/get_visitor_count" in event["resource"]:
        try:
            total_visitors = get_visitor_count(pk="total", sk="historic")
            daily_visitors = get_visitor_count(pk="daily", sk=current_date)

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
                    "message": "Could not get visitor from table."
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
