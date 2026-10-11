import os, hashlib, time, threading
import boto3
from botocore.exceptions import ClientError

_table=boto3.resource("dynamodb",region_name=os.environ.get("AWS_REGION","ap-south-1")).Table(os.environ.get("DDB_CHUNK_TABLE", "neetwise_chunk_stats"))

PENALTY_WEIGHT=float(os.environ.get("FB_WEIGHT","1.0"))
MIN_VOTES=3
SMOOTHING=5
REFRESH_SECONDS=600

_stats,_last_refresh,_lock={},0.0,threading.Lock()

def chunk_id(doc):
    return hashlib.sha1(doc.page_content.encode("utf-8")).hexdigest()[:16]

def record_votes(chunk_ids,rating):
    field="ups" if rating==1 else "downs"
    for cid in set(chunk_ids):
        try:
            _table.update_item(
                Key={"chunk_id":cid},
                UpdateExpression=f"ADD {field} :one",
                ExpressionAttributeValues={":one":1},
            )
        except ClientError as e:
            print(f"[chunk_stats] record_votes failed: {e}")

def _refresh():
    global _stats,_last_refresh
    try:
        items,kwargs=[],{}
        while True:
            resp=_table.scan(**kwargs)
            items+=resp["Items"]
            if "LastEvaluatedKey" not in resp:
                break
            kwargs["ExclusiveStartKey"]=resp["LastEvaluatedKey"]
        new={i["chunk_id"]: (int(i.get("ups", 0)), int(i.get("downs", 0))) for i in items}
        with _lock:
            _stats=new
    except ClientError as e:
        print(f"[chunk_stats] refresh failed: {e}")
    _last_refresh=time.time()

def adjustment(doc):
    if time.time()-_last_refresh>REFRESH_SECONDS:
        _refresh()
    ups, downs=_stats.get(chunk_id(doc), (0, 0))
    n=ups + downs
    if n < MIN_VOTES:
        return 0.0
    return -PENALTY_WEIGHT*(downs-ups)/(n+SMOOTHING)

def rerank_with_feedback(scored):
    out=[(doc, raw, raw + adjustment(doc)) for doc, raw in scored]
    out.sort(key=lambda x: x[2], reverse=True)
    return out