# 載入LineBot所需要的模組
import re
import os
import psycopg2
from linebot.models import *
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from flask import Flask, request, abort, render_template
from linebot.models.responses import Content

app = Flask(__name__)

# 必須放上自己的Channel Access Token
line_bot_api = LineBotApi('/Suqku7M9ZSE0fAymS2Z2ZDWlbqs5UfK2Gdl+/GPFTIPxpa6G3cL1lDeY0XdKTWU/IIduz9bVNO8Tev6W0+rt5F406ivy4J9K/7XZ5+l4S0lcLLaU/lauYRwoaOxkPcJeQWUDf/lvGLPeC+bdIG8EwdB04t89/1O/w1cDnyilFU=')

# 必須放上自己的Channel Secret
handler = WebhookHandler('f633360451f8659118a5fbbef0e218d0')


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

# handle text message
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    if "記錄" in msg:
        try:
            record_list = prepare_record(msg)
            result = insert_record(record_list)

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=result)
            )
        except:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="資料上傳失敗")
            )
#     elif "查詢" in msg:
#         result = select_record()

#         line_bot_api.reply_message(
#             event.reply_token,
#             TextSendMessage(text=result)
#         )
#     elif "刪除" in msg:
#         result = delete_record(msg)

#         line_bot_api.reply_message(
#             event.reply_token,
#             TextSendMessage(text=result)
#         ) 
#     elif "更新" in msg:
#         result = update_record(msg)

#         line_bot_api.reply_message(
#             event.reply_token,
#             TextSendMessage(text=result)
#         ) 
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg)
        )

def prepare_record(msg):
    text_list = msg.split('@')
    record_list = []

    for i in text_list[1:]:
        temp_list = i.split(" ")

        userid = temp_list[0]
        writingdate = temp_list[1]
        diary = temp_list[2]

        record = (userid, writingdate, diary)
        record_list.append(record)

    return record_list

# 將資料匯入資料庫
def insert_record(record_list):
    DATABASE_URL = os.environ["DATABASE_URL"]

    conn = psycopg2.connect(database="dahggat84j3plu",
						    user="fmhvtfdwhmriha",
						    password="6fa7397e002c2217f7975b7fe04e8348d7f14966c49137f500b6e9ba3f22b796",
						    host="ec2-35-175-68-90.compute-1.amazonaws.com",
						    port="5432")
    cursor = conn.cursor()

    table_columns = "(userid, writingdate, diary)"
    postgres_insert_query = f"""INSERT INTO userdiary {table_columns} VALUES (%s,%s,%s)"""

    try:
        cursor.executemany(postgres_insert_query, record_list)
    except:
        cursor.execute(postgres_insert_query, record_list)

    conn.commit()

    # 要回傳的文字
    message = f"{cursor.rowcount}筆資料成功匯入資料庫囉"

    cursor.close()
    conn.close()

    return message

#主程式
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
