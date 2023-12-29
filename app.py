from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import hashlib
import os
import json

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

def validate_signature(request_body, received_signature, secret_key):
    # 使用 SHA-1 算法生成簽名
    signature = hashlib.sha1((request_body + secret_key).encode()).hexdigest()
    return signature == received_signature

@app.route("/callback", methods=['POST'])
def callback():
    # 獲取 LINE 的 X-Line-Signature 標頭值
    signature = request.headers['X-Line-Signature']

    # 獲取請求體作為文本
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 處理 webhook 請求體
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@app.route("/webhook", methods=['POST'])
def webhook():
    # 從環境變量獲取秘密鑰匙
    secret_key = os.getenv('SECRET_KEY')
    if not secret_key:
        abort(500, 'Server configuration error')

    # 獲取原始請求體和簽名
    request_body = request.get_data(as_text=True)
    received_signature = request.headers.get('x-chatbase-signature')

    # 驗證簽名
    if not validate_signature(request_body, received_signature, secret_key):
        abort(400, 'Invalid signature')

    # 解析 JSON 數據
    try:
        data = json.loads(request_body)
        # 處理數據...
        print(data)
    except json.JSONDecodeError:
        abort(400, 'Invalid JSON')

    return 'OK'

# LINE Bot 處理 TextMessage 的功能
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    # 在這裡處理接收到的訊息...
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
