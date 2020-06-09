from django.contrib import admin
from .models import Account, Item, Transaction

admin.site.register(Account)
admin.site.register(Item)
admin.site.register(Transaction)
