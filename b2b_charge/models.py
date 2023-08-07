from django.db import models
from django.db.transaction import atomic
from django.db.models import Sum


class BaseModel(models.Model):
    """
    The base model which is abstract and provides the base fields.
    """

    updated_time = models.DateTimeField(verbose_name="Updated Datetime", auto_now=True)
    created_time = models.DateTimeField(
        verbose_name="Created Datetime", auto_now_add=True
    )

    class Meta:
        abstract = True


class Merchant(BaseModel):
    """
    The model for the B2B Merchant.
    """

    credit = models.IntegerField(verbose_name="Merchant Credit", default=0)
    is_active = models.BooleanField(verbose_name="Is active", default=True)

    @classmethod
    def create_merchant(cls, initial_credit=0):
        """
        A factory method which returns merchant objects.
        """
        if initial_credit < 0:
            raise Exception(
                "create_merchant: Negative Credits happened. Cannot Continue."
            )
        merchant = Merchant(credit=initial_credit)
        merchant.save()
        return merchant

    def get_credit(self):
        """
        Returns the overall credit of the merchant.
        """
        return self.credit

    def add_credit(self, credit):
        """
        Adds credit to the merchant.
        """
        if self.credit + credit < 0:
            raise Exception("add_credit: Negative Credits happened. Cannot Continue.")
        self.credit += credit
        self.save()

    def subtract_credit(self, credit):
        """
        Subtracts merchant's credit.
        """
        if self.credit - credit < 0:
            raise Exception(
                "subtract_credit: Negative Credits happened. Cannot Continue. %d - %d. merchant_id: %d, merchant_credits: %d"
                % (self.credit, credit, self.id, self.get_credit())
            )
        self.credit -= credit
        self.save()

    @atomic
    def transaction(self, action, phone, amount):
        """
        The method that executes the transaction and log in atomic fashion.
        """
        if action == "add_credit":
            self.add_credit(amount)
            TransactionLog(merchant_id=self.id, phone=None, amount=amount).log()
        elif action == "subtract_credit":
            self.subtract_credit(amount)
            amount = amount * -1
            TransactionLog(merchant_id=self.id, phone=phone, amount=amount).log()


class TransactionLog(BaseModel):
    """
    The model for the Transaction Log
    """

    merchant = models.ForeignKey(
        Merchant, on_delete=models.CASCADE, verbose_name="Merchant"
    )
    phone = models.BigIntegerField(verbose_name="Phone Number", null=True)
    amount = models.IntegerField(verbose_name="Charge Amount", default=0)

    def log(self):
        """
        logs the transaction.
        """
        self.save()

    @classmethod
    def get_merchant_credit_sum(cls, merchant):
        """
        Gets the sum of all transactions for a particular merchant using the logs.
        """
        merchant_transactionlogs_sum = cls.objects.filter(merchant=merchant).aggregate(
            Sum("amount")
        )["amount__sum"]
        return merchant_transactionlogs_sum
