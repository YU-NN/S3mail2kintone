import json
import urllib.parse
import base64
import boto3
import os
import botocore
import requests
import time

s3 = boto3.resource("s3")
client = s3.meta.client


#Lambdaに保存した環境変数を取得
KINTONE_URL = "https://{kintone_domain}/k/v1/record.json"
url = KINTONE_URL.format(
   kintone_domain=os.environ["KINTONE_DOMAIN"],
   kintone_app=os.environ["KINTONE_APP"]
)
headers_key = os.environ["KINTONE_HEADERS_KEY"]
api_key = os.environ["KINTONE_API_KEY"]
headers = {headers_key: api_key}
headers["Content-Type"] = "application/json"


body_post_jsonfile = open("body_post.json","r")
body_post_dic      = json.load(body_post_jsonfile)



def lambda_handler(event, context):


    #バケット取得、キー取得。
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(event["Records"][0]["s3"]["object"]["key"], encoding="utf-8")

    try:
        time.sleep(0.2)
        response = client.get_object(Bucket=bucket,Key=key)
        mail = response["Body"].read().decode("utf-8")

        #"envelope-from="以降の文字列を取得して、”;”でfrom_addressを取得する。
        encoded_subject = mail.split("Subject: ")[1].split("\r\n")[0]
        subject = ""
        if("=?utf-8?B?" in encoded_subject):
            encoded_subject = encoded_subject.split("=?utf-8?B?")[1].split("?=")[0]
            subject         = (base64.b64decode(encoded_subject)).decode("utf-8")
        else:
            subject = encoded_subject


        date            = mail.split("Date: ")[1].split("References:")[0].split("\r\n")[0]
        to_adress       = mail.split("To: ")[1].split("In-Reply")[0].split("\r\n")[0]
        from_address    = mail.split("envelope-from=")[1].split(";")[0]
        encoded_body    = mail.split("\r\n\r\n")[1].split("\r\n")[0]

        try:
            body        = (base64.b64decode(encoded_body)).decode("utf-8").split("\r\n\r\n")[0]
        except Exception as e:
            body        = encoded_body


    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            logger.error("The object does not exist.")
        else:
            raise e



    body_post_dic["record"]["Subject"]["value"]         = subject
    body_post_dic["record"]["FromEmailAdress"]["value"] = from_address
    body_post_dic["record"]["ToEmailAdress"]["value"]   = to_adress
    body_post_dic["record"]["Timestamp"]["value"]       = date
    body_post_dic["record"]["Contents"]["value"]        = body


    result = RecordPost2kintone(url, headers, body_post_dic)
    return result









def RecordPost2kintone(url, headers, post_record_dic):
    resp = requests.post(url, data=json.dumps(post_record_dic), headers=headers)
    record_data = json.loads(resp.text)
    return record_data
