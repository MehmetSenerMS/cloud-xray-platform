from locust import HttpUser, task, between


class CloudXRayUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        response = self.client.post(
            "/auth/login",
            json={
                "email": "mehmetaws@test.com",
                "password": "GiresunKesap28*"
            }
        )

        token_data = response.json()
        self.access_token = token_data["access_token"]

        self.headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

    @task
    def get_transaction_history(self):
        self.client.get(
            "/transactions/history",
            headers=self.headers
        )