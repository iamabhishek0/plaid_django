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


client = plaid.Client(client_id = PLAID_CLIENT_ID, secret=PLAID_SECRET,
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
        public_token = create_public_token()['public_token']
        try:
            exchange_response = client.Item.public_token.exchange(public_token)
            serializer = AccessToken(data=exchange_response)
            if serializer.is_valid():
                if Item.objects.filter(user=self.request.user).count() == 0:
                    item = Item.objects.create(access_token=serializer.validated_data['access_token'],
                                               item_id=serializer.validated_data['item_id'],
                                               user=self.request.user
                                               )
                    item.save()

        except plaid.errors.PlaidError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(data=exchange_response, status=status.HTTP_200_OK)


class get_transaction(APIView):
    def post(self, request):
        item = Item.objects.filter(user=self.request.user)
        if item.count() > 0:
            access_token = item.values('access_token')[0]['access_token']

            # transaction of two years i.e. 730 days
            start_date = '{:%Y-%m-%d}'.format(datetime.datetime.now() + datetime.timedelta(-730))
            end_date = '{:%Y-%m-%d}'.format(datetime.datetime.now())

            try:
                transactions_response = client.Transactions.get(access_token, start_date, end_date)
            except plaid.errors.PlaidError as e:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            return Response(data=transactions_response, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def webhook(request):
    return HttpResponse('Webhook received', status=status.HTTP_202_ACCEPTED)