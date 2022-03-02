import re
import os

from database import *
from linebot.models import *
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from flask import Flask, request, abort, render_template


app = Flask(__name__)

Channel_Access_Token = '/Suqku7M9ZSE0fAymS2Z2ZDWlbqs5UfK2Gdl+/GPFTIPxpa6G3cL1lDeY0XdKTWU/IIduz9bVNO8Tev6W0+rt5F406ivy4J9K/7XZ5+l4S0lcLLaU/lauYRwoaOxkPcJeQWUDf/lvGLPeC+bdIG8EwdB04t89/1O/w1cDnyilFU='
line_bot_api    = LineBotApi(Channel_Access_Token)
Channel_Secret  = 'f633360451f8659118a5fbbef0e218d0'
handler = WebhookHandler(Channel_Secret)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body      = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

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
    elif "查詢" in msg:
        result = select_record()

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result)
        )
    elif "刪除" in msg:
        result = delete_record(msg)

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result)
        ) 
    elif "更新" in msg:
        result = update_record(msg)

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result)
        ) 
    else:
        print("Wrong")


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
