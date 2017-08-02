import json
import requests
from requests.auth import HTTPBasicAuth
from ..settings import PAYPAL_CLIENT_ID, PAYPAL_SECRET, PAYPAL_SECURITY_USERID, \
    PAYPAL_SECURITY_PASSWORD, PAYPAL_SECURITY_SIGNATURE, PAYPAL_APPLICATION_ID, \
    PAYPAL_FEE_GENESIS_PERCENT, PAYPAL_GENESIS_PAYMENT_ACCOUNT, PAYPAL_HOST_REDIRECT_URL
from ..settings import PAYPAL_LIVE_MODE as paypal_mode
from ..core.orders.models import PayTransactions, PaymentCredential, Order
from ..tasks import sent_order_information_notification


class PayPal:
    def __init__(self):
        pass

    if paypal_mode:  # Live
        paypal_host_url = 'https://api.paypal.com/v1/'
        paypal_adaptive_pay_host_url = 'https://svcs.paypal.com/AdaptivePayments'
    else:  # Sandboxpaypal_mode
        paypal_host_url = 'https://api.sandbox.paypal.com/v1/'
        paypal_adaptive_pay_host_url = 'https://svcs.sandbox.paypal.com/AdaptivePayments'

    addaptive_headers = {
            'X-PAYPAL-SECURITY-USERID': PAYPAL_SECURITY_USERID,
            'X-PAYPAL-SECURITY-PASSWORD': PAYPAL_SECURITY_PASSWORD,
            'X-PAYPAL-SECURITY-SIGNATURE': PAYPAL_SECURITY_SIGNATURE,
            'X-PAYPAL-APPLICATION-ID': PAYPAL_APPLICATION_ID,
            'X-PAYPAL-REQUEST-DATA-FORMAT': 'JSON',
            'X-PAYPAL-RESPONSE-DATA-FORMAT': 'JSON',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/39.0.2171.95 Safari/537.36'
        }

    def get_access_token(self):
        paypal_url = self.paypal_host_url + 'oauth2/token'
        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en_US',
            'content-type': 'application/x-www-form-urlencoded'
        }
        params = {
            'grant_type': 'client_credentials'
        }
        response = requests.post(
            paypal_url,
            headers=headers,
            params=params,
            auth=HTTPBasicAuth(PAYPAL_CLIENT_ID, PAYPAL_SECRET)
        )
        response_json = json.loads(response.text)
        return response_json['access_token']

    def execute_payment(self, payment_id, payer_id):
        access_token = self.get_access_token()
        paypal_url = self.paypal_host_url + 'payments/payment/' + payment_id + '/execute/'
        headers = {
            'Authorization': 'Bearer ' + access_token,
            'Accept-Language': 'en_US',
            'content-type': 'application/json'
        }
        params = {
            'payer_id': payer_id
        }
        response = requests.post(paypal_url, json=params, headers=headers, params=params)
        response_json = json.loads(response.text)
        return response_json

    def create_parallel_payment(self, order):
        amount_payment = order.full_price
        genesis_tax = round(amount_payment * (PAYPAL_FEE_GENESIS_PERCENT/100), 2)
        amount_recipient = round(amount_payment-genesis_tax, 2)
        seller_email = PaymentCredential.objects.get(owner=order.seller).payment_email
        pay_transaction = PayTransactions.objects.create(
            order=order,
            payer=order.user,
            recipient=order.seller,
            recipient_transactions_email=seller_email,
            tax_recipient=PAYPAL_GENESIS_PAYMENT_ACCOUNT,
            tax_percent=PAYPAL_FEE_GENESIS_PERCENT,
            amount=amount_payment,
            amount_recipient=amount_recipient,
            amount_genesis_tax=genesis_tax
        )
        params = {
            'actionType': 'PAY',
            "cancelUrl": PAYPAL_HOST_REDIRECT_URL + "/api/payment/cancel",
            'currencyCode': 'USD',
            'receiverList': {
                'receiver': [
                    {'amount': amount_recipient, 'email': seller_email},
                    {'amount': genesis_tax, 'email': PAYPAL_GENESIS_PAYMENT_ACCOUNT}
                ]
            },
            'requestEnvelope': {
                'errorLanguage': 'en_US',
                'detailLevel': 'ReturnAll'
            },
            "returnUrl": PAYPAL_HOST_REDIRECT_URL + "/api/payment/redirect",
            'feesPayer': 'EACHRECEIVER',
            'reverseAllParallelPaymentsOnError': True,
            'memo': 'Payment in Genesis App',
        }

        response_json = requests.post(
            url=self.paypal_adaptive_pay_host_url+'/Pay',
            data=json.dumps(params),
            headers=self.addaptive_headers
        ).json()

        if 'error' in response_json:
            pay_transaction.transaction_status = 'ERROR'
            pay_transaction.save()
            return False
        pay_transaction.transaction_status = response_json['paymentExecStatus']
        if response_json['responseEnvelope']['ack'] == 'Success':
            pay_key = response_json['payKey']
            pay_transaction.pay_key = pay_key
            pay_transaction.timestamp = response_json['responseEnvelope']['timestamp']
            pay_transaction.save()
            # return 'https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_ap-payment&paykey=' + pay_key
            return 'https://www.sandbox.paypal.com/webapps/adaptivepayment/flow/pay?paykey=' + pay_key + '&expType=mini'
        else:
            pay_transaction.save()
            return False

    def check_parallel_payment_status(self, pay_key):
        try:
            pay_transaction = PayTransactions.objects.get(pay_key=pay_key)
        except:
            return {}

        params = {
            "payKey": pay_transaction.pay_key,
            "requestEnvelope": {
                "errorLanguage": "en_US"
            }
        }
        response_json = requests.post(self.paypal_adaptive_pay_host_url + '/PaymentDetails', data=json.dumps(params), headers=self.addaptive_headers).json()
        if 'senderEmail' in response_json:
            pay_transaction.payer_transaction_email = response_json['senderEmail']
        if 'status' in response_json:
            pay_status = response_json['status']
            pay_transaction.transaction_status = pay_status
            if pay_status == 'COMPLETED':
                order = Order.objects.get(pk=pay_transaction.order_id)
                if order.status == 0:
                    order.status = 1
                    order.save()
                    sent_order_information_notification.delay(order.id)
        pay_transaction.save()
        return {}

    def paypal_account_information(self, paypal_email):
        params = {
            'emailAddress': paypal_email,
            'matchCriteria': 'NONE',
            'requestEnvelope'""'requestEnvelope': {
                'errorLanguage': 'en_US',
                'detailLevel': 'ReturnAll'
            }
        }
        url = "https://svcs.sandbox.paypal.com/AdaptiveAccounts/GetVerifiedStatus"
        response_json = requests.post(url=url, data=json.dumps(params), headers=self.addaptive_headers).json()
        return response_json
