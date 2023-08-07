from django.contrib import admin
from .models import Merchant, TransactionLog
# Register your models here.

admin.site.register(Merchant)
admin.site.register(TransactionLog)