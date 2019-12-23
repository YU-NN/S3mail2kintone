import json
import urllib.parse
import base64
import boto3
import os

s3 = boto3.client('s3')


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
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')



    try:
        #レスポンスを取得するにはS3の読み取り権限がある実行ロールが必要
        response = s3.get_object(Bucket=bucket, Key=key)
        mail = response['Body'].read().replace('\n','').replace('\r','')
        #"envelope-from="以降の文字列を取得して、”;”でfrom_addressを取得する。
        from_address = mail.split('envelope-from=')[1].split(';')[0]
        subject = mail.split('Subject: ')[1].split('To: ')[0]
        body = base64.b64decode(mail.split('base64')[1].split('--')[0])
        html_body = base64.b64decode(mail.split('base64')[2].split('--')[0])


    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e



    body_post_dic["record"]["Subject"]["value"]         = subject
    body_post_dic["record"]["FromEmailAdress"]["value"] = from_address
    #body_post_dic["record"]["ToEmailAdress"]["value"]   = event["Records"][0]["ses"]["mail"]["commonHeaders"]["to"][0]
    #body_post_dic["record"]["Timestamp"]["value"]       = event["Records"][0]["ses"]["mail"]["commonHeaders"]["date"]
    body_post_dic["record"]["Contents"]["value"]        = body


    result = RecordPost2kintone(url, headers, body_post_dic)
    return result




def RecordPost2kintone(url, headers, post_record_dic):
    resp = requests.post(url, data=json.dumps(post_record_dic), headers=headers)
    #resp = requests.post(url, data=post_record_dic, headers=headers)
    record_data = json.loads(resp.text)
    return record_data
