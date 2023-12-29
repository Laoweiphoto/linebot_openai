from flask import Flask, request, abort
import hashlib
import os
import json

app = Flask(__name__)

def validate_signature(request_body, received_signature, secret_key):
    # 使用 SHA-1 算法生成簽名
    signature = hashlib.sha1((request_body + secret_key).encode()).hexdigest()
    return signature == received_signature

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

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
