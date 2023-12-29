from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import tempfile, os
import datetime
import time
import traceback
import requests

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

def chatbase_response(text):
    # 設定 Chatbase 請求
    url = "https://www.chatbase.co/api/v1/some-endpoint" # 替換為實際的 Chatbase 端點
    headers = {
        "Authorization": "Bearer " + os.getenv('CHATBASE_SECRET_KEY'),
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    data = {"message": text} # 根據實際情況調整 payload 結構
    response = requests.post(url, headers=headers, json=data)
    
    # 處理回應
    if response.status_code == 200:
        return response.json() # 根據實際情況調整解析方式
    else:
        return "發生錯誤：" + response.text

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    try:
        chatbase_answer = chatbase_response(msg)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(chatbase_answer))
    except Exception as e:
        print(traceback.format_exc())
        line_bot_api.reply_message(event.reply_token, TextSendMessage('發生錯誤，請稍後再試'))

# 其他處理函數...

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
