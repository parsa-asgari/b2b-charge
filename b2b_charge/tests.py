from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.shortcuts import get_object_or_404
from .models import Merchant, TransactionLog
from .serializers import MerchantSerializer, TransactionLogSerializer

import random


class MerchantTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.data_1 = {"merchant_id": Merchant.create_merchant().id, "credit": 1000000}
        self.data_2 = {"merchant_id": Merchant.create_merchant().id, "credit": 1200000}

    def add_credit_two_times(self, data):
        """
        Helper function. Adds credits to a given merchant two times.
        Credit amounts are randomized.
        """
        merchant_credit = 0
        for i in range(2):
            random_number = int(random.random() * 10)
            data["credit"] *= random_number
            response = self.client.post(
                reverse("merchant-list") + str(data['merchant_id']) + "/add-credit/", data=data
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            merchant_credit += data['credit']
        return merchant_credit
    
    def subtract_credit_ten_times(self, data):
        """
        Helper function. Buys charge using a given merchant ten times.
        Charge amounts are randomized.
        """
        merchant_credit = 0
        for i in range(10):
            random_amount = random.choice([1000, 2000, 5000, 10000, 20000])
            random_phone = random.choice([1,2,3,4,5])
            data = {
                "merchant_id" : data['merchant_id'],
                'phone' : random_phone,
                'amount': random_amount
            }
            response = self.client.post(
                reverse("merchant-list") + str(data['merchant_id']) + "/buy-charge/", data=data
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            merchant_credit -= data['amount']
        return merchant_credit

    def test_merchant_add_credit_normal(self):
        # Merchant 1
        merchant_1_credit = self.add_credit_two_times(data=self.data_1)
        merchant_get_response = self.client.get(
            reverse("merchant-list") + str(self.data_1['merchant_id']) + "/get-credit/", data=self.data_1
        )
        self.assertEqual(merchant_get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(merchant_get_response.data['merchant_id'], self.data_1['merchant_id'])  
        self.assertEqual(merchant_get_response.data['credit'], merchant_1_credit)

        # Merchant 2
        merchant_2_credit = self.add_credit_two_times(data=self.data_2)
        merchant_get_response = self.client.get(
            reverse("merchant-list") + str(self.data_2['merchant_id']) + "/get-credit/", data=self.data_2
        )
        self.assertEqual(merchant_get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(merchant_get_response.data['merchant_id'], self.data_2['merchant_id'])  
        self.assertEqual(merchant_get_response.data['credit'], merchant_2_credit)

    def test_merchant_add_credit_abnormal(self):
        """
        
        """
        random_number = int(random.random() * 10)
        data = self.data_1
        data['credit'] *= -1 * random_number
        response = self.client.post(
                reverse("merchant-list") + str(data['merchant_id']) + "/add-credit/", data=data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_transactionlog_sum(self):

        # Merchant 1
        merchant_1_added_credits = self.add_credit_two_times(data=self.data_1)
        merchant_1_bought_charges = self.subtract_credit_ten_times(data=self.data_1)
        merchant_get_response = self.client.get(
                reverse("merchant-list") + str(self.data_1['merchant_id']) + "/get-credit/", data=self.data_1
        )
        self.assertEqual(merchant_get_response.status_code, status.HTTP_200_OK)

        merchant_1 = get_object_or_404(Merchant ,id=self.data_1['merchant_id'])
        merchant_1_credit_sum = TransactionLog.get_merchant_credit_sum(merchant=merchant_1)
        self.assertEqual(merchant_1_credit_sum, merchant_1_added_credits+merchant_1_bought_charges)

        # Merchant 2
        merchant_2_added_credits = self.add_credit_two_times(data=self.data_2)
        merchant_2_bought_charges = self.subtract_credit_ten_times(data=self.data_2)
        merchant_get_response = self.client.get(
                reverse("merchant-list") + str(self.data_2['merchant_id']) + "/get-credit/", data=self.data_2
        )
        self.assertEqual(merchant_get_response.status_code, status.HTTP_200_OK)

        merchant_2 = get_object_or_404(Merchant, id=self.data_2['merchant_id'])
        merchant_2_credit_sum = TransactionLog.get_merchant_credit_sum(merchant=merchant_2)
        self.assertEqual(merchant_2_credit_sum, merchant_2_added_credits+merchant_2_bought_charges)