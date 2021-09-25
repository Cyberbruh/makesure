import requests
import time
import os

<<<<<<< Updated upstream
=======
from .payout import PayoutStatus

from .deposit import DepositStatus

CHATEX_API_LINK = "https://api.staging.iserverbot.ru/v1"
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
    request = requests.get('https://api.chatex.com/v1/payment-systems', headers=request_headers)
    return request.json()[:10]
=======
    request = requests.get(CHATEX_API_LINK+'/payment-systems', headers=request_headers)
    return request.json()[:10]

async def getPaymentLink(deposit):
    await check_auth()
    request_headers = {"Authorization": "Bearer " + CHATEX_ACCESS_TOKEN}
    request_data = {
        "fiat_amount": deposit.dispute.amount,
        "coin": "BTC",
        "country_code": "RUS",
        "fiat": "RUB",
        "lang_id": "RU",
        "payment_system_id": deposit.method,
    }
    request = requests.post(CHATEX_API_LINK+'/invoices', json=request_data, headers=request_headers)
    data = request.json()
    deposit.invoice_id = data['id']
    deposit.payment_url = data['payment_url']
    deposit.status = DepositStatus.LINK_SENT
    #deposit.save()
    return deposit

async def updatePayment(deposit):
    if(deposit.invoice_id is None):
        raise Exception('Empty invoice ID, found bug')
    await check_auth()
    request_headers = {"Authorization": "Bearer " + CHATEX_ACCESS_TOKEN}
    request = requests.get(CHATEX_API_LINK+'/invoices/'+deposit.invoice_id, headers=request_headers)
    data = request.json()
    if(data['status'] == "COMPLETED"):
        deposit.status = DepositStatus.SUCCESS
        deposit.save()
    elif(data['status'] == "CANCELED"):
        deposit.status = DepositStatus.CANCELED
        deposit.save()
    return deposit

async def makePayout(payout):
    await check_auth()
    request_headers = {"Authorization": "Bearer " + CHATEX_ACCESS_TOKEN}
    request_data = {
        "pair": "btc/rub",
        "fiat_amount": payout.amount,
        "payment_details": payout.data,
        "payment_system_id": payout.method,
    }
    request = requests.get(CHATEX_API_LINK+'/payouts', json=request_data, headers=request_headers)
    data = request.json()
    payout.payout_id = data['id']
    if(data['status'] == "FAILED"):
        payout.description = data['cancelation_reason']
        payout.status = PayoutStatus.FAILED
    else:
        payout.status = PayoutStatus.PENDING
    payout.save()
    return payout

#async def updatePayout
>>>>>>> Stashed changes
