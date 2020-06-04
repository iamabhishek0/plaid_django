import json
import os
import plaid
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


# Fill in your Plaid API keys - https://dashboard.plaid.com/account/keys
PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')
PLAID_PUBLIC_KEY = os.getenv('PLAID_PUBLIC_KEY')
# Use 'sandbox' to test with Plaid's Sandbox environment (username: user_good,
# password: pass_good)
# Use `development` to test with live users and credentials and `production`
# to go live
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')
# PLAID_PRODUCTS is a comma-separated list of products to use when initializing
# Link. Note that this list must contain 'assets' in order for the app to be
# able to create and retrieve asset reports.
PLAID_PRODUCTS = os.getenv('PLAID_PRODUCTS', 'transactions')

# PLAID_COUNTRY_CODES is a comma-separated list of countries for which users
# will be able to select institutions from.
PLAID_COUNTRY_CODES = os.getenv('PLAID_COUNTRY_CODES', 'US')

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
        "institution_id": "ins_10",
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
        except plaid.errors.PlaidError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(data=exchange_response, status=status.HTTP_200_OK)
