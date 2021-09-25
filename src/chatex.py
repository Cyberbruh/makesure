import requests
import time
import os
from datetime import datetime, timedelta

from .deposit import DepositStatus

CHATEX_API_LINK = "https://api.staging.iserverbot.ru/v1"
stop_api = False
CHATEX_ACCESS_TOKEN = ''
ACCESS_TOKEN_DATE = None

async def check_auth():
    global stop_api
    global CHATEX_ACCESS_TOKEN
    global ACCESS_TOKEN_DATE
    while(stop_api):
        time.sleep(1)
    if(ACCESS_TOKEN_DATE is None or datetime.now()-ACCESS_TOKEN_DATE > timedelta(0, 1800, 0)):
        stop_api = True
        token_request_headers = {"Authorization": "Bearer " + os.environ.get('CHATEX_REFRESH_TOKEN')}
        token_request = requests.post(CHATEX_API_LINK+'/auth/access-token', headers=token_request_headers)
        if(token_request.status_code != 200):
            raise Exception('Wrong REFRESH_TOKEN')
        CHATEX_ACCESS_TOKEN = token_request.json()['access_token']
        ACCESS_TOKEN_DATE = datetime.now()
        stop_api = False

async def getPaymentMethods():
    tmp = {
        {
            "id": 347,
            "name": "QIWI"
        },
        {
            "id": 347,
            "name": "Webmoney"
        },
        {
            "id": 347,
            "name": "Sberbank"
        },
        {
            "id": 347,
            "name": "Payoneer"
        },
        {
            "id": 347,
            "name": "Ю.Мани"
        },
    }
    await check_auth()
    return tmp
    # request_headers = {"Authorization": "Bearer " + CHATEX_ACCESS_TOKEN}
    # request = requests.get(CHATEX_API_LINK+'/payment-systems', headers=request_headers)
    # if(request.status_code != 200):
    #     print(request, request.text)
    #     raise Exception("Can't get payment methods")
    # return request.json()

async def getPaymentLink(deposit):
    await check_auth()
    request_headers = {"Authorization": "Bearer " + CHATEX_ACCESS_TOKEN}
    request_data = {
        "fiat_amount": deposit.dispute.amount,
        "coin": "btc",
        "country_code": "RUS",
        "fiat": "rub",
        "lang_id": "RU",
        "payment_system_id": deposit.method,
    }
    request = requests.post(CHATEX_API_LINK+'/invoices', json=request_data, headers=request_headers)
    if(request.status_code != 201):
        print(request_data, request, request.text)
        raise Exception("Can't get payment link")
    data = request.json()
    deposit.invoice_id = data['id']
    deposit.payment_url = data['payment_url']
    deposit.status = DepositStatus.LINK_SENT
    deposit.save()
    return deposit

async def updatePayment(deposit):
    if(deposit.invoice_id is None):
        raise Exception('Empty invoice ID, found bug')
    await check_auth()
    request_headers = {"Authorization": "Bearer " + CHATEX_ACCESS_TOKEN}
    request = requests.get(CHATEX_API_LINK+'/invoices/'+deposit.invoice_id, headers=request_headers)
    if(request.status_code != 200):
        print(request, request.text)
        raise Exception("Can't update payment")
    data = request.json()
    if(data['status'] == "COMPLETED"):
        deposit.status = DepositStatus.SUCCESS
        deposit.coin_amount = float(data['amount'])
        deposit.save()
    elif(data['status'] == "CANCELED"):
        deposit.status = DepositStatus.CANCELED
        deposit.save()
    return deposit

async def makePayout(payout):
    await check_auth()
    request_headers = {"Authorization": "Bearer " + CHATEX_ACCESS_TOKEN}
    request_data = {
        "coin": "btc",
        "amount": payout.amount,
        "recipient": payout.data
    }
    request = requests.post(CHATEX_API_LINK+'/wallet/transfers', json=request_data, headers=request_headers)
    if(request.status_code != 200):
        print(request_data, request, request.text)
        raise Exception("Can't make payout")