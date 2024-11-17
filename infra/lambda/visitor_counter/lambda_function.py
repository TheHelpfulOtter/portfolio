import json
import urllib
import boto3
import os
from botocore.exceptions import ClientError
from aws_lambda_powertools import Logger
from datetime import datetime

dynamodb_resource = boto3.resource("dynamodb", region_name="eu-west-1")
TABLE = dynamodb_resource.Table(os.environ["TABLE"])

def add_visitor_to_table() -> None:
    try:
        current_time = datetime.now()
        current_date = current_time.strftime("%Y-%m-%d")

        updates = [
            # Daily counter
            {
                "Key": {"pk": "daily_", "sk": current_date},
                "UpdateExpression": "ADD visitors :inc",
                "ExpressionAttributeValues": {":inc": 1}
            },
            # Total counter
            {
                "Key": {"pk": "total_", "sk": "historic"},
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


def get_visitor_count() -> int | None:
    try:
        response = TABLE.get_item(
            Key={
                "pk": "total_",
                "sk": "historic"
            }
        )
        
        item = response.get("Item", {})
        total_visitors = item.get("visitors", 0) 

        logger.info("Total visitors retrieved.")
        logger.info(total_visitors)

        return total_visitors
    
    except Exception as e:
        logger.info(str(e))

        return None


def lambda_handler(event, context):
    logger.info(event)

    if "resource" in event and "/add_visitor" in event:
        try:
            add_visitor_to_table()

        except Exception as e:
            logger.info(str(e))

            return "Could not add visitor to table."
        
    elif "resource" in event and "/get_visitor_count" in event:
        try:
            get_visitor_count()

        except Exception as e:
            logger.info(str(e))

            return "Could not get visitor from table."

    logger.info(event)

    return {
        "status": "complete"
    }
