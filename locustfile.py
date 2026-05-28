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
        
        if response.status_code != 200:
            print("LOGIN FAILED:", response.status_code, response.text[:300])
            return

        try:
            token_data = response.json()
        except Exception:
            print("LOGIN NON-JSON RESPONSE:", response.status_code, response.text[:300])
            return
        
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
            "/prediction/predict",
            json=self.predict_payload,
            headers=self.headers
        )