from django.contrib import admin
from .models import Merchant, TransactionLog

# Register your models here.


class BaseAdmin(admin.ModelAdmin):
    list_display = [
        "__str__",
        "created_time",
        "updated_time",
    ]
    list_filter = []

    def get_list_display_links(self, request, list_display):
        return self.get_list_display(request)


@admin.register(Merchant)
class MerchantAdmin(BaseAdmin):
    list_display = [
        "__str__",
        "credit",
        "is_active",
        "created_time",
        "updated_time",
    ]

@admin.register(TransactionLog)
class TransactionLogAdmin(BaseAdmin):
    list_display = [
        "__str__",
        "phone",
        "amount",
        "created_time",
        "updated_time",
    ]