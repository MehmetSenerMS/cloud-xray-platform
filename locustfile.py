from locust import HttpUser, task, between
import json


class CloudXRayPredictUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.ready = False
        self.headers = {}
        self.predict_payload = None

        response = self.client.post(
            "/auth/login",
            json={
                "email": "mehmetaws@test.com",
                "password": "GiresunKesap28*"
            },
            name="/auth/login"
        )

        if response.status_code != 200:
            print("LOGIN FAILED:", response.status_code, response.text[:300])
            return

        try:
            token_data = response.json()
        except Exception:
            print("LOGIN NON-JSON RESPONSE:", response.status_code, response.text[:300])
            return

        access_token = token_data.get("access_token")

        if not access_token:
            print("LOGIN RESPONSE HAS NO ACCESS TOKEN:", token_data)
            return

        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        try:
            with open("/mnt/locust/predict_payload.json", "r") as f:
                self.predict_payload = json.load(f)
        except Exception as e:
            print("PAYLOAD LOAD FAILED:", str(e))
            return

        self.ready = True

    @task
    def predict(self):
        if not self.ready or self.predict_payload is None:
            return

        with self.client.post(
            "/prediction/predict",
            json=self.predict_payload,
            headers=self.headers,
            name="/prediction/predict",
            catch_response=True
        ) as response:
            if response.status_code >= 400:
                response.failure(
                    f"HTTP {response.status_code}: {response.text[:300]}"
                )