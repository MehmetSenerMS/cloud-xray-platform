from locust import HttpUser, task, between
import json


class CloudXRayPredictUser(HttpUser):
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

        self.headers = {
            "Authorization": f"Bearer {token_data['access_token']}",
            "Content-Type": "application/json"
        }

        with open("/mnt/locust/predict_payload.json", "r") as f:
            self.predict_payload = json.load(f)

    @task
    def predict(self):
        self.client.post(
            "/predict",
            json=self.predict_payload,
            headers=self.headers
        )