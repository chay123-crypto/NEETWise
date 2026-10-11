from datetime import datetime, timezone
import uuid
import os
import boto3
from boto3.dynamodb.conditions import Key
from chunk_stats import record_votes

TABLE_NAME=os.environ.get("DDB_TABLE","neetwise_feedback")
REGION = os.environ.get("AWS_REGION", "ap-south-1")

_table=boto3.resource("dynamodb", region_name=REGION).Table(TABLE_NAME)
def _now():
    return datetime.now(timezone.utc).isoformat()

def new_message_id():
    return str(uuid.uuid4())

def log_interaction(message_id,kind,question,answer,citations=None,Lang=None,mode=None,chunk_ids=None):
    try:
        _table.put_item(Item={
            'message_id':message_id,
            'question':question,
            'answer':answer,
            'citations':citations,
            'kind of question':kind,
            'language':Lang,
            "chunk_ids":chunk_ids or [],
            'answer_mode':mode,
            'created_at':_now(),
        })
    except Exception as e:
        print({'error':f'Logging failed action failed {e}'})

def save_feedback(message_id,rating,comments=""):
    try:
        response=_table.update_item(
            Key={"message_id":message_id},
            UpdateExpression="SET rating=:r,rating_key=:k,#c=:c,feedback_at=:t",
            ExpressionAttributeNames={"#c":"comment"},
            ExpressionAttributeValues={
                    ":r":rating,
                    ":k":"UP" if rating==1 else "DOWN",
                    ":c":comments[:1000],
                    ":t":_now(),
                },
            ConditionExpression="attribute_exists(message_id) AND attribute_not_exists(rating)",
            ReturnValues="ALL_NEW",
        )
        record_votes(response['Attributes'].get("chunk_ids",[]),rating)
        return True
    except Exception as e:
        print({'error':f'Error so action failed {e}'})
        return False

def get_feedback(rating_key="DOWN",limit=200):
    resp=_table.query(
        IndexName="rating-index",
        KeyConditionExpression=Key("rating_key").eq(rating_key),
        ScanIndexForward=False,
        Limit=limit
    )
    return resp["Items"]
