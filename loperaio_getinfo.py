
goo_email_body ="依頼車輌： メルセデス・ベンツ Ｍ・ベンツ ＣＬＡ１８０　ＡＭＧスタイル　ＡＭＧプレミアムＰＫＧ　禁煙\n"\
"年式： 2018年\n"\
"走行距離： 1.1万K\n"\
"価格： 285.9万円\n"\
"カラー： ポーラーホワイト\n"\
"お名前： 本部\n"\
"住所： 埼玉県戸田市"

def GetInfo(goo_email_body,info):
    return goo_email_body.split(info)[1].split("\n")[0]

car_type  = GetInfo(goo_email_body,"依頼車輌： ")
car_age   = GetInfo(goo_email_body,"年式： ")
car_run   = GetInfo(goo_email_body,"走行距離： ")
car_price = GetInfo(goo_email_body,"価格： ")
car_color = GetInfo(goo_email_body,"カラー： ")

customer_name   = GetInfo(goo_email_body,"お名前： ")
customer_adress = GetInfo(goo_email_body,"住所： ")
print(car_type)
print(car_age)
print(car_run)
print(car_price)
print(car_color)
print(customer_name)
print(customer_adress)
