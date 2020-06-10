from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from plaid_django.settings import LOGIN_REDIRECT_URL
from .keys import *
from .models import Item


@login_required(login_url=LOGIN_REDIRECT_URL)
def index(request):
    keys = {
        'plaid_public_key': PLAID_PUBLIC_KEY,
        'plaid_environment': PLAID_ENV,
        'plaid_products': PLAID_PRODUCTS,
        'plaid_country_codes': PLAID_COUNTRY_CODES,

    }
    return render(request, "oauth.html", context=keys)


@login_required(login_url=LOGIN_REDIRECT_URL)
def home(request):
    items = Item.objects.filter(user=request.user)
    return render(request, 'home.html', {'items': items})


def loginview(request):
    return render(request, "login.html")
