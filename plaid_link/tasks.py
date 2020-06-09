# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
import datetime
import plaid
from .keys import *
from .models import Account, Item, Transaction


client = plaid.Client(client_id=PLAID_CLIENT_ID, secret=PLAID_SECRET,
                      public_key=PLAID_PUBLIC_KEY, environment=PLAID_ENV, api_version='2019-05-29')


@shared_task
def add(x, y):
    return x + y


@shared_task
def fetch_transactions(access_token):
    # transaction of two years i.e. 730 days
    start_date = '{:%Y-%m-%d}'.format(
        datetime.datetime.now() + datetime.timedelta(-730))
    end_date = '{:%Y-%m-%d}'.format(datetime.datetime.now())
    transactions_response = client.Transactions.get(
        access_token, start_date, end_date)

    accounts = transactions_response['accounts']
    transactions = transactions_response['transactions']
    item_id = transactions_response['item']['item_id']

    for account in accounts:
        account_obj = Account.objects.filter(account_id=account['account_id'])
        if(account_obj.count() > 0):
            for a in account_obj:
                a.balance_available = account['balances']['available']
                a.balance_current = account['balances']['current']
                a.save()

        else:
            # item = Item.objects.filter(access_token=access_token)[0]
            item = Item.objects.filter(item_id=item_id)[0]
            account_obj = Account.objects.create(
                item=item,
                account_id=account['account_id'],
                balance_available=account['balances']['available'],
                balance_current=account['balances']['current'])

            account_obj.save()

    for transaction in transactions:
        transaction_obj = Transaction.objects.filter(
            transaction_id=transaction['transaction_id'])
        if(transaction_obj.count() > 0):
            for a in account_obj:
                a.amount = transaction['amount']
                a.pending = transaction['pending']
                a.save()

        else:
            account_ = Account.objects.filter(
                account_id=transaction['account_id'])[0]
            transaction_obj = Transaction.objects.create(
                transaction_id=transaction['transaction_id'],
                account=account_,
                amount=transaction['amount'],
                date=transaction['date'],
                name=transaction['name'],
                pending=transaction['pending'])

            transaction_obj.save()
