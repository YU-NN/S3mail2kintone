import json
import urllib.parse
import base64
import boto3
import os
import botocore
import requests
import time
import email
from email.header import decode_header

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


body_post_jsonfile = open("body4loperaio.json","r")
body_post_dic      = json.load(body_post_jsonfile)



def lambda_handler(event, context):


    #バケット取得、キー取得。
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(event["Records"][0]["s3"]["object"]["key"], encoding="utf-8")

    try:
        time.sleep(0.2)
        response = client.get_object(Bucket=bucket,Key=key)
        email_body   = response["Body"].read().decode("utf-8")
        email_obj = email.message_from_string(email_body)

        body = ""
        attach_fname = ""
        attach_file_list = []

        for part in email_obj.walk():
            # ContentTypeがmultipartの場合は実際のコンテンツはさらに
            # 中のpartにあるので読み飛ばす
            if part.get_content_maintype() == 'multipart':
                continue
            # ファイル名の取得
            attach_fname = part.get_filename()
            # ファイル名がない場合は本文のはず
            if not attach_fname:
                charset = str(part.get_content_charset())
                if charset:
                    body += part.get_payload(decode=True).decode(charset, errors="replace")
                else:
                    body += part.get_payload(decode=True)
            else:
                # ファイル名があるならそれは添付ファイルなので
                # データを取得する
                attach_file_list.append({
                    "name": attach_fname,
                    "data": part.get_payload(decode=True)
                })


    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            logger.error("The object does not exist.")
        else:
            raise e


    body_post_dic["app"] = os.environ["KINTONE_APP"]

    body_post_dic["record"]["email_body"]["value"]          = body.split("<html><head><meta http-equiv=")[0]


    result = RecordPost2kintone(url, headers, body_post_dic)
    return result


def get_decoded_header(email_message,key_name):
    ret = ""
    raw_obj = email_message.get(key_name)
    if raw_obj is None:
        return ""
    # デコードした結果をunicodeにする
    for fragment, encoding in decode_header(raw_obj):
        if not hasattr(fragment, "decode"):
            ret += fragment
            continue
        # encodeがなければとりあえずUTF-8でデコードする
        if encoding:
            ret += fragment.decode(encoding)
        else:
            ret += fragment.decode("UTF-8")
    return ret









def RecordPost2kintone(url, headers, post_record_dic):
    resp = requests.post(url, data=json.dumps(post_record_dic), headers=headers)
    record_data = json.loads(resp.text)
    return record_data
