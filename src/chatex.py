import requests
import time
import os

stop_api = False
CHATEX_ACCESS_TOKEN = ''

async def check_auth():
    global stop_api
    global CHATEX_ACCESS_TOKEN
    while(stop_api):
        time.sleep(1)
    check_request_headers = {"Authorization": "Bearer " + CHATEX_ACCESS_TOKEN}
    check_request = requests.get('https://api.chatex.com/v1/invoices', headers=check_request_headers)
    if(check_request.status_code != 200):
        stop_api = True
        token_request_headers = {"Authorization": "Bearer " + os.environ.get('CHATEX_REFRESH_TOKEN')}
        token_request = requests.post('https://api.chatex.com/v1/auth/access-token', headers=token_request_headers)
        CHATEX_ACCESS_TOKEN = token_request.json()['access_token']
        stop_api = False

async def getPaymentMethods():
    global CHATEX_ACCESS_TOKEN
    await check_auth()
    request_headers = {"Authorization": "Bearer " + CHATEX_ACCESS_TOKEN}
    request = requests.get('https://api.chatex.com/v1/payment-systems', headers=request_headers)
    return request.json()[:10]