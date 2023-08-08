from locust import HttpUser, task


class QuickstartUser(HttpUser):
    @task
    def buy_charge(self):
        self.client.post(
            "/api/v1/merchant/1/buy-charge/", json={"phone": 9120000000, "amount": 100}
        )
