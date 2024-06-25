import requests
import json

class XRobixClient:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.access_token = None
        self.refresh_token = None
        self.headers = {
            'Content-Type': 'application/json'
        }
        self.login()

    def login(self):
        url = f"{self.base_url}/auth/login"
        payload = {
            'username': self.username,
            'password': self.password
        }
        response = requests.post(url, data=payload, headers=self.headers)
        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens['access_token']
            self.headers['Authorization'] = f'Bearer {self.access_token}'
            self.refresh_token = response.cookies.get('refresh_token')
        else:
            raise Exception(f"Login failed: {response.json().get('error', 'Unknown error')}")

    def refresh_access_token(self):
        url = f"{self.base_url}/auth/refresh_token"
        response = requests.post(url, headers=self.headers, cookies={'refresh_token': self.refresh_token})
        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens['access_token']
            self.headers['Authorization'] = f'Bearer {self.access_token}'
        else:
            raise Exception(f"Token refresh failed: {response.json().get('error', 'Unknown error')}")

    def submit_task(self, task_data):
        url = f"{self.base_url}/tasks"
        response = requests.post(url, json=task_data, headers=self.headers)
        if response.status_code == 401:
            self.refresh_access_token()
            response = requests.post(url, json=task_data, headers=self.headers)
        return response.json()

    def control_task(self, task_id, action):
        url = f"{self.base_url}/tasks"
        params = {
            'task_id': task_id,
            'action': action
        }
        response = requests.put(url, params=params, headers=self.headers)
        if response.status_code == 401:
            self.refresh_access_token()
            response = requests.put(url, params=params, headers=self.headers)
        return response.json()

    def get_task_status(self, task_id):
        url = f"{self.base_url}/tasks/{task_id}/status"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 401:
            self.refresh_access_token()
            response = requests.get(url, headers=self.headers)
        return response.json()

    def get_task_updates(self, task_id):
        url = f"{self.base_url}/tasks/{task_id}/status/updates"
        response = requests.get(url, headers=self.headers, stream=True)
        if response.status_code == 401:
            self.refresh_access_token()
            response = requests.get(url, headers=self.headers, stream=True)
        for line in response.iter_lines():
            if line:
                yield line.decode('utf-8')

    def list_tasks(self, page=1, limit=10):
        url = f"{self.base_url}/tasks/list"
        params = {
            'page': page,
            'limit': limit
        }
        response = requests.get(url, params=params, headers=self.headers)
        if response.status_code == 401:
            self.refresh_access_token()
            response = requests.get(url, params=params, headers=self.headers)
        return response.json()

    def register_webhook(self, webhook_data):
        url = f"{self.base_url}/tasks/webhooks"
        response = requests.post(url, json=webhook_data, headers=self.headers)
        if response.status_code == 401:
            self.refresh_access_token()
            response = requests.post(url, json=webhook_data, headers=self.headers)
        return response.json()
