# 載入LineBot所需要的模組
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import os
from database import *

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
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg)
        )

#主程式
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
