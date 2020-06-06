from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Item(models.Model):
    access_token = models.CharField(max_length=100)
    item_id = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
