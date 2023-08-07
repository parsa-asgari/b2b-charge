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
        self.test_data_init()

    def test_data_init(self):
        merchant_1_id = Merchant.create_merchant().id
        merchant_2_id = Merchant.create_merchant().id
        self.data_1 = {"merchant_id": merchant_1_id, "credit": 1000000}
        self.data_2 = {"merchant_id": merchant_2_id, "credit": 1200000}

    def add_credit_x_times(self, x, data):
        """
        Helper function. Adds credits to a given merchant two times.
        Credit amounts are randomized.
        """
        merchant_credit = 0
        for i in range(x):
            response = self.client.post(
                reverse("merchant-list") + str(data["merchant_id"]) + "/add-credit/",
                data=data,
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            merchant_credit += data["credit"]
        return merchant_credit

    def subtract_credit_x_times(self, x, data):
        """
        Helper function. Buys charge using a given merchant ten times.
        Charge amounts are randomized.
        """
        merchant_credit = 0
        for i in range(x):
            random_amount = random.choice([1000, 2000, 5000, 10000, 20000])
            random_phone = random.choice([1, 2, 3, 4, 5])
            data = {
                "merchant_id": data["merchant_id"],
                "phone": random_phone,
                "amount": random_amount,
            }
            response = self.client.post(
                reverse("merchant-list") + str(data["merchant_id"]) + "/buy-charge/",
                data=data,
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            merchant_credit -= data["amount"]
        return merchant_credit

    def test_merchant_add_credit_normal(self):
        """
        tests the <add-credit> endpoint for normal positive amounts.
        """
        # Merchant 1
        merchant_1_credit = self.add_credit_x_times(x=2, data=self.data_1)
        merchant_get_response = self.client.get(
            reverse("merchant-list") + str(self.data_1["merchant_id"]) + "/get-credit/",
            data=self.data_1,
        )
        self.assertEqual(merchant_get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            merchant_get_response.data["merchant_id"], self.data_1["merchant_id"]
        )
        self.assertEqual(merchant_get_response.data["credit"], merchant_1_credit)

        # Merchant 2
        merchant_2_credit = self.add_credit_x_times(x=2, data=self.data_2)
        merchant_get_response = self.client.get(
            reverse("merchant-list") + str(self.data_2["merchant_id"]) + "/get-credit/",
            data=self.data_2,
        )
        self.assertEqual(merchant_get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            merchant_get_response.data["merchant_id"], self.data_2["merchant_id"]
        )
        self.assertEqual(merchant_get_response.data["credit"], merchant_2_credit)

    def test_merchant_add_credit_negative_amount(self):
        """
        tests the <add-credit> endpoint for negative amounts.
        """
        # Merchant1
        data = self.data_1
        data["credit"] *= -1
        response = self.client.post(
            reverse("merchant-list") + str(data["merchant_id"]) + "/add-credit/",
            data=data,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Merchant2
        data = self.data_2
        data["credit"] *= -1
        response = self.client.post(
            reverse("merchant-list") + str(data["merchant_id"]) + "/add-credit/",
            data=data,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_buy_charge(self):
        """
        adds credits to the merchants, then buys charge.
        Lastly, checks to see if the <get-credit> returns the right credit compared to the actions done so far.
        """
        # Merchant 1
        merchant_1_added_credits = self.add_credit_x_times(x=2, data=self.data_1)
        merchant_1_bought_charges = self.subtract_credit_x_times(x=10, data=self.data_1)
        merchant_get_response = self.client.get(
            reverse("merchant-list") + str(self.data_1["merchant_id"]) + "/get-credit/",
            data=self.data_1,
        )
        self.assertEqual(merchant_get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            merchant_get_response.json()["credit"],
            merchant_1_added_credits + merchant_1_bought_charges,
        )

        # Merchant 2
        merchant_2_added_credits = self.add_credit_x_times(x=2, data=self.data_2)
        merchant_2_bought_charges = self.subtract_credit_x_times(x=10, data=self.data_2)
        merchant_get_response = self.client.get(
            reverse("merchant-list") + str(self.data_2["merchant_id"]) + "/get-credit/",
            data=self.data_2,
        )
        self.assertEqual(merchant_get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            merchant_get_response.json()["credit"],
            merchant_2_added_credits + merchant_2_bought_charges,
        )

    def test_buy_charge_negative_case(self):
        """
        adds credits to the merchants, then buys charge.
        The charge buying function is set to exhaust the merchant's credits. So that, it would throw an exception.

        If the exception is generated, this test succeeds. Else, it fails
        """
        # Merchant 1
        try:
            self.add_credit_x_times(x=2, data=self.data_1)
            self.subtract_credit_x_times(x=1000, data=self.data_1)
            self.fail()
        except:
            self.assertEqual(1, 1)

        # Merchant 2
        try:
            self.add_credit_x_times(x=2, data=self.data_2)
            self.subtract_credit_x_times(x=1000, data=self.data_2)
            self.fail()
        except:
            self.assertEqual(1, 1)

    def test_transactionlog_sum(self):
        """
        Generates data for Merchant1 and Merchant2 using self.setUp().
        Then, checks to see if the response of the <get-credit> endpoint and the calculted sum using the logs match.
        """
        # Merchant 1
        merchant_1_added_credits = self.add_credit_x_times(x=2, data=self.data_1)
        merchant_1_bought_charges = self.subtract_credit_x_times(x=10, data=self.data_1)
        merchant_get_response = self.client.get(
            reverse("merchant-list") + str(self.data_1["merchant_id"]) + "/get-credit/",
            data=self.data_1,
        )
        self.assertEqual(merchant_get_response.status_code, status.HTTP_200_OK)

        merchant_1 = get_object_or_404(Merchant, id=self.data_1["merchant_id"])
        merchant_1_credit_sum = TransactionLog.get_merchant_credit_sum(
            merchant=merchant_1
        )
        self.assertEqual(
            merchant_1_credit_sum, merchant_1_added_credits + merchant_1_bought_charges
        )

        # Merchant 2
        merchant_2_added_credits = self.add_credit_x_times(x=2, data=self.data_2)
        merchant_2_bought_charges = self.subtract_credit_x_times(x=10, data=self.data_2)
        merchant_get_response = self.client.get(
            reverse("merchant-list") + str(self.data_2["merchant_id"]) + "/get-credit/",
            data=self.data_2,
        )
        self.assertEqual(merchant_get_response.status_code, status.HTTP_200_OK)

        merchant_2 = get_object_or_404(Merchant, id=self.data_2["merchant_id"])
        merchant_2_credit_sum = TransactionLog.get_merchant_credit_sum(
            merchant=merchant_2
        )
        self.assertEqual(
            merchant_2_credit_sum, merchant_2_added_credits + merchant_2_bought_charges
        )


        # Phase 2

    def test_merchant_add_credit_normal_phase2(self):
        """
        tests the <add-credit> endpoint for normal positive amounts.

        phase 2
        """
        # Merchant 1
        merchant_1_credit = self.add_credit_x_times(x=10, data=self.data_1)
        merchant_get_response = self.client.get(
            reverse("merchant-list") + str(self.data_1["merchant_id"]) + "/get-credit/",
            data=self.data_1,
        )
        self.assertEqual(merchant_get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            merchant_get_response.data["merchant_id"], self.data_1["merchant_id"]
        )
        self.assertEqual(merchant_get_response.data["credit"], merchant_1_credit)

        # Merchant 2
        merchant_2_credit = self.add_credit_x_times(x=10, data=self.data_2)
        merchant_get_response = self.client.get(
            reverse("merchant-list") + str(self.data_2["merchant_id"]) + "/get-credit/",
            data=self.data_2,
        )
        self.assertEqual(merchant_get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            merchant_get_response.data["merchant_id"], self.data_2["merchant_id"]
        )
        self.assertEqual(merchant_get_response.data["credit"], merchant_2_credit)


    def test_buy_charge_phase2(self):
        """
        adds credits to the merchants, then buys charge.
        Lastly, checks to see if the <get-credit> returns the right credit compared to the actions done so far.
        """
        # Merchant 1
        merchant_1_added_credits = self.add_credit_x_times(x=10, data=self.data_1)
        merchant_1_bought_charges = self.subtract_credit_x_times(x=1000, data=self.data_1)
        merchant_get_response = self.client.get(
            reverse("merchant-list") + str(self.data_1["merchant_id"]) + "/get-credit/",
            data=self.data_1,
        )
        self.assertEqual(merchant_get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            merchant_get_response.json()["credit"],
            merchant_1_added_credits + merchant_1_bought_charges,
        )

        # Merchant 2
        merchant_2_added_credits = self.add_credit_x_times(x=10, data=self.data_2)
        merchant_2_bought_charges = self.subtract_credit_x_times(x=1000, data=self.data_2)
        merchant_get_response = self.client.get(
            reverse("merchant-list") + str(self.data_2["merchant_id"]) + "/get-credit/",
            data=self.data_2,
        )
        self.assertEqual(merchant_get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            merchant_get_response.json()["credit"],
            merchant_2_added_credits + merchant_2_bought_charges,
        )