import datetime
import json
import plaid
import requests
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AccessToken
from .keys import *
from .models import Item
from .tasks import delete_transactions, fetch_transactions


client = plaid.Client(client_id=PLAID_CLIENT_ID, secret=PLAID_SECRET,
                      public_key=PLAID_PUBLIC_KEY, environment=PLAID_ENV, api_version='2019-05-29')


def create_public_token():
    """
    Generates Public token.
    Returns : A Dictionary with keys 'public_token' and 'request_id'
    """
    url = "https://sandbox.plaid.com/sandbox/public_token/create"
    headers = {'content-type': 'application/json'}
    payload = {
        "institution_id": "ins_5",
        "public_key": PLAID_PUBLIC_KEY,
        "initial_products": ["transactions"]
    }
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    return r.json()


class get_access_token(APIView):
    """
    Exchanges Public token for access token
    """

    def post(self, request):
        request_data = request.POST
        public_token = request_data.get('public_token')
        # public_token = create_public_token()['public_token']
        try:
            exchange_response = client.Item.public_token.exchange(public_token)
            serializer = AccessToken(data=exchange_response)
            if serializer.is_valid():
                access_token = serializer.validated_data['access_token']
                item = Item.objects.create(access_token=access_token,
                                           item_id=serializer.validated_data['item_id'],
                                           user=self.request.user
                                           )
                item.save()

                # Async Task
                fetch_transactions.delay(access_token)

        except plaid.errors.PlaidError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(data=exchange_response, status=status.HTTP_200_OK)


class get_transaction(APIView):
    def post(self, request):
        item = Item.objects.filter(user=self.request.user)
        if item.count() > 0:
            access_token = item.values('access_token')[0]['access_token']

            # transactions of two years i.e. 730 days
            start_date = '{:%Y-%m-%d}'.format(
                datetime.datetime.now() + datetime.timedelta(-730))
            end_date = '{:%Y-%m-%d}'.format(datetime.datetime.now())

            try:
                transactions_response = client.Transactions.get(
                    access_token, start_date, end_date)
            except plaid.errors.PlaidError as e:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            return Response(data={'error': None, 'transactions': transactions_response}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class get_identity(APIView):
    def get(self, request):
        item = Item.objects.filter(user=self.request.user)
        if item.count() > 0:
            access_token = item.values('access_token')[0]['access_token']
            try:
                identity_response = client.Identity.get(access_token)
            except plaid.errors.PlaidError as e:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            return Response(data={'error': None, 'identity': identity_response}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class get_balance(APIView):
    def get(self, request):
        item = Item.objects.filter(user=self.request.user)
        if item.count() > 0:
            access_token = item.values('access_token')[0]['access_token']
            try:
                balance_response = client.Accounts.balance.get(access_token)
            except plaid.errors.PlaidError as e:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            return Response(data={'error': None, 'balance': balance_response}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class get_item_info(APIView):
    def get(self, request):
        item = Item.objects.filter(user=self.request.user)
        if item.count() > 0:
            access_token = item.values('access_token')[0]['access_token']
            try:
                item_response = client.Item.get(access_token)
                institution_response = client.Institutions.get_by_id(
                    item_response['item']['institution_id'])
            except plaid.errors.PlaidError as e:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            return Response(data={'error': None, 'item': item_response['item'], 'institution': institution_response['institution']}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class get_account_info(APIView):
    def get(self, request):
        item = Item.objects.filter(user=self.request.user)
        if item.count() > 0:
            access_token = item.values('access_token')[0]['access_token']
            try:
                accounts_response = client.Accounts.get(access_token)
            except plaid.errors.PlaidError as e:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            return Response(data={'accounts': accounts_response, 'error': None, }, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


@csrf_exempt
def webhook(request):
    request_data = request.POST
    webhook_type = request_data.get('webhook_type')
    webhook_code = request_data.get('webhook_code')

    if webhook_type == 'TRANSACTIONS':
        item_id = request_data.get('item_id')
        if webhook_code == 'TRANSACTIONS_REMOVED':
            removed_transactions = request_data.get('removed_transactions')
            delete_transactions.delay(item_id, removed_transactions)

        else:
            new_transactions = request_data.get('new_transactions')
            fetch_transactions.delay(None, item_id, new_transactions)

    return HttpResponse('Webhook received', status=status.HTTP_202_ACCEPTED)
