#載入LineBot所需要的模組
# coding = utf-8
from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
from snownlp import SnowNLP
from opencc import OpenCC
import statistics
import psycopg2
import re
import os

app = Flask(__name__)
 
# 必須放上自己的Channel Access Token
line_bot_api = LineBotApi('/Suqku7M9ZSE0fAymS2Z2ZDWlbqs5UfK2Gdl+/GPFTIPxpa6G3cL1lDeY0XdKTWU/IIduz9bVNO8Tev6W0+rt5F406ivy4J9K/7XZ5+l4S0lcLLaU/lauYRwoaOxkPcJeQWUDf/lvGLPeC+bdIG8EwdB04t89/1O/w1cDnyilFU=')
# 必須放上自己的Channel Secret
handler = WebhookHandler('f633360451f8659118a5fbbef0e218d0')

# conn = psycopg2.connect(database="dahggat84j3plu",
# 			user="fmhvtfdwhmriha",
# 			password="6fa7397e002c2217f7975b7fe04e8348d7f14966c49137f500b6e9ba3f22b796",
# 			host="ec2-35-175-68-90.compute-1.amazonaws.com",
# 			port="5432")

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

#訊息傳遞區塊
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = text=event.message.text
    if "寫日記" in message:
        record_list = prepare_record(message)
        result = insert_record(record_list)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=result))
    elif "查詢" in message:
        result = select_record()
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=result))
    elif "更新" in message:
        result = update_record(message)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=result))
#     elif "情緒分數" in message:
#         image_message = ImageSendMessage(
#             original_content_url='https://imgur.com/a/6yuwnTL',
#             preview_image_url='https://imgur.com/a/6yuwnTL'
#         )
#         line_bot_api.reply_message(event.reply_token, image_message)
    elif "使用者" in message:
        link = 'http://10.1.4.189:5000/app_test/{}'
        message = {user_id(message)}
        for i in message:
            result = link.format(i)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(message))

def user_id(message):
    characters = "使用者"

    for x in range(len(characters)):
        message = message.replace(characters[x],"")

    return message      
      
def prepare_record(message):
    text_list = message.split('\n')   

    record_list = []

    for i in text_list[1:]:
        temp_list = i.split(" ")

        userid = temp_list[0]
        writingdate = temp_list[1]
        diary = temp_list[2]
        score = diary_to_score(diary)
        
        record = (userid, writingdate, diary, score)
        record_list.append(record)
        
    return record_list	

# 將資料匯入資料庫
def insert_record(record_list):
    DATABASE_URL = os.environ["DATABASE_URL"]
    
    conn   = psycopg2.connect(DATABASE_URL, sslmode="require")
    cursor = conn.cursor()

    table_columns = "(userid, writingdate, diary, score)"
    postgres_insert_query = f"""INSERT INTO userdiary {table_columns} VALUES (%s,%s,%s,%s)"""

    try:
        cursor.executemany(postgres_insert_query, record_list)
    except:
        cursor.execute(postgres_insert_query, record_list)
    
    conn.commit()

    # 要回傳的文字
    message = f"{cursor.rowcount}筆日記成功新增至日記庫囉"

    cursor.close()
    conn.close()

    return message

# 查詢資料
def select_record():
    DATABASE_URL = os.environ["DATABASE_URL"]

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    postgres_select_query = f"""SELECT * FROM userdiary ORDER BY id"""

    cursor.execute(postgres_select_query)
    record = str(cursor.fetchall())

    content = ""
    record = record.split("),")

    for number, r in enumerate(record):
        content += f"第{number+1}筆資料\n{r}\n"

    cursor.close()
    conn.close()

    return content   

# 更新資料
def update_record(message):
    DATABASE_URL = os.environ["DATABASE_URL"]

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    msg_list = message.split(" ")
    column   = msg_list[1]
    origin   = msg_list[2]
    new      = msg_list[3]
    
    postgres_update_query = f"""UPDATE userdiary set {column} = %s WHERE {column} = %s"""

    cursor.execute(postgres_update_query, (new, origin))
    conn.commit()

    content = ""

    count = cursor.rowcount
    content += f"{count}筆資料成功從日記庫更新囉"

    return content   

def diary_to_score(diary):
    cc = OpenCC('tw2sp')
    a = cc.convert(diary)
    sentence = re.split('，|。|…', a)
    s_list = []
    for i in sentence:
        s = SnowNLP(i)
        s_senti = s.sentiments
        s_round_senti = round(s_senti, 1)
        s_list.append(s_round_senti)
    score = round(statistics.mean(s_list), 1)
    
    return score
   
#主程式
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
