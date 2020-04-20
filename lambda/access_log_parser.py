import base64
import datetime
import gzip
import json
import re

import boto3

bucket_name = 'central-log'

nginx_log_format = re.compile(
    r"""(?P<remote>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) (?P<host>.+) (?P<user>.+) \[(?P<datetime>\d{2}\/[a-z]{3}\/\d{4}:\d{2}:\d{2}:\d{2} (\+|\-)\d{4})\] ((\"(?P<method>.+) )(?P<path>.+)(http\/[1-2]\.[0-9]")) (?P<code>\d{3}) (?P<size>\d+) (["](?P<refferer>(\-)|(.+))["]) (["](?P<agent>.+)["])""",
    re.IGNORECASE)
log_keys = ['remote', 'host', 'user', 'datetime', 'method', 'path', 'code', 'size', 'referer', 'agent']


def handler(event, context):
    body = ""
    for record in event['Records']:
        payload = base64.b64decode(record['kinesis']['data'])
        log = json.loads(payload)
        if 'message' in log:
            parsed = parse_log(log['message'])
            body += json.dumps(parsed) + "\n"
    print(body)
    return upload_s3(body)


def parse_log(log):
    parsed = {}
    data = re.search(nginx_log_format, log).groupdict()
    if data:
        for key in log_keys:
            if key in data:
                parsed[key] = data[key]
    return parsed


def upload_s3(body):
    now = datetime.datetime.now()
    key_name = now.strftime('access_log/year=%Y/month=%m/day=%d/access_log_%H%M%S.json.gz')
    s3 = boto3.client('s3', endpoint_url='http://localhost:4572')
    try:
        # Add a file to your Object Store
        response = s3.put_object(
            Bucket=bucket_name,
            Key=key_name,
            Body=gzip.compress(bytes(body, 'utf-8'))
        )
        print(response)
    except Exception as e:
        raise IOError(e)
    return response
