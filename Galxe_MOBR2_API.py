from flask import Flask, jsonify, abort, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, resources={r"/wallet-info/$address": {"origins": "https://galxe.com"}})
WHITELISTED_IPS = {'35.185.209.0', '35.203.155.18'}

# JSON Data Loading...
def fetch_json_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Week4 Data
def get_Week4_info(user_account, data):
    TradingVolume = data['competition']['notionalVolume']
    PnL = data['competition']['pnl']
    TradingCount = data['competition']['tradeCount']
    user_account = user_account.lower()
    account_list = list(TradingVolume.keys())
    if user_account in account_list:
        return {
            'Pnl': round(PnL[user_account],2),
            'Notional Volume': round(TradingVolume[user_account],2),
            'Trade Count': TradingCount[user_account]
        }
    return None

def ip_whitelisted(f):
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        if client_ip not in WHITELISTED_IPS:
            abort(403)  # 허용되지 않은 IP 주소로부터의 접근인 경우 403 에러 반환
        return f(*args, **kwargs)
    return decorated_function

@app.route('/wallet-info/$address')
@ip_whitelisted
def wallet_info(wallet_address):
    url = 'https://moby-data-testnet.s3.ap-northeast-2.amazonaws.com/competition-data.json'
    data = fetch_json_data(url)

    if data:
        user_data = get_Week4_info(wallet_address, data)
        if user_data:
            return jsonify(user_data)
        else:
            return jsonify({'message': 'Wallet address not found'}), 404
    else:
        return jsonify({'message': 'Failed to fetch data'}), 500

if __name__ == '__main__':
    app.run(debug=True)
