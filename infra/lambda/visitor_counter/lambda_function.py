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
DEV_URL = os.environ["DEV_URL"]
BASE_URL = os.environ["BASE_URL"]

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
        logger.error(f"Error updating table: {str(e)}")
        return None


def get_visitor_count(pk: str, sk: str) -> int | None:
    try:
        logger.info("Getting visitor count")
        response = TABLE.get_item(
            Key={
                "pk": pk,
                "sk": sk
            }
        )
        logger.debug(response)
        
        item = response.get("Item", {})
        visitors = item.get("visitors", 0) 

        logger.info(f"Retrieved {visitors} visitors")
        return visitors
    
    except Exception as e:
        logger.error(f"Error getting visitor count: {str(e)}")
        return None


def lambda_handler(event, context):
    logger.info(event)
    
    # Get the origin from headers
    headers = event.get('headers', {})
    origin = headers.get('origin', '')
    
    # List of allowed origins
    allowed_origins = [
        DEV_URL,  # Local development
        BASE_URL  # Production site
    ]
    
    # Set CORS headers based on origin
    response_headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Headers": "Content-Type,Origin",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
    }
    
    # Only allow specific origins
    if origin in allowed_origins:
        response_headers["Access-Control-Allow-Origin"] = origin
    else:
        return {
            "statusCode": 403,
            "headers": response_headers,
            "body": json.dumps({
                "message": "Unauthorized origin"
            })
        }

    current_time = datetime.now()
    current_date = current_time.strftime("%Y-%m-%d")

    if "resource" in event and "add_visitor" in event["resource"]:
        try:
            add_visitor_to_table(current_date=current_date)

            return {
                "statusCode": 200,
                "headers": response_headers,
                "body": json.dumps({
                    "message": "Added visitors."
                })
            }

        except Exception as e:
            logger.error(f"Error in add_visitor endpoint: {str(e)}")
            return {
                "statusCode": 500,
                "headers": response_headers,
                "body": json.dumps({
                    "message": "Could not add visitor to table."
                })
            }
        
    elif "resource" in event and "/get_visitor_count" in event["resource"]:
        try:
            total_visitors = int(get_visitor_count(pk="total", sk="historic"))
            daily_visitors = int(get_visitor_count(pk="daily", sk=current_date))

            return {
                "statusCode": 200,
                "headers": response_headers,
                "body": json.dumps({
                    "total_visitors": total_visitors,
                    "daily_visitors": daily_visitors
                })
            }

        except Exception as e:
            logger.error(f"Error in get_visitor_count endpoint: {str(e)}")
            return {
                "statusCode": 500,
                "headers": response_headers,
                "body": json.dumps({
                    "message": "Could not get visitor from table."
                })
            }

    logger.info("Invalid endpoint called")
    return {
        "statusCode": 400,
        "headers": response_headers,
        "body": json.dumps({
            "message": "Invalid endpoint"
        })
    }
