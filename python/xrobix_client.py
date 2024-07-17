import requests
import aiohttp
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        logger.debug(f"Logging in with URL: {url} and payload: {payload}")
        response = requests.post(url, data=payload, headers=headers)
        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens['access_token']
            self.headers['Authorization'] = f'Bearer {self.access_token}'
            logger.debug(f"Login successful, access_token: {self.access_token}")
        else:
            error_message = response.json().get('error', response.text)
            logger.error(f"Login failed: {error_message}")
            raise Exception(f"Login failed: {error_message}")

    def refresh_access_token(self):
        url = f"{self.base_url}/auth/refresh_token"
        logger.debug(f"Refreshing access token with URL: {url}")
        response = requests.post(url, headers=self.headers)
        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens['access_token']
            self.headers['Authorization'] = f'Bearer {self.access_token}'
            logger.debug(f"Token refresh successful, new access_token: {self.access_token}")
        else:
            error_message = response.json().get('error', response.text)
            logger.error(f"Token refresh failed: {error_message}")
            raise Exception(f"Token refresh failed: {error_message}")

    def submit_task(self, task_data):
        url = f"{self.base_url}/tasks"
        logger.debug(f"Submitting task with URL: {url} and task_data: {task_data}")
        response = requests.post(url, json=task_data, headers=self.headers)
        if response.status_code == 401:
            logger.warning("Access token expired, refreshing token.")
            self.refresh_access_token()
            response = requests.post(url, json=task_data, headers=self.headers)
        logger.debug(f"Task submission response: {response.json()}")
        return response.json()

    def control_task(self, task_id, action):
        url = f"{self.base_url}/tasks/{task_id}/exec"
        payload = {"action": action}
        logger.debug(f"Controlling task with URL: {url} and payload: {payload}")
        response = requests.put(url, json=payload, headers=self.headers)
        if response.status_code == 401:
            logger.warning("Access token expired, refreshing token.")
            self.refresh_access_token()
            response = requests.put(url, json=payload, headers=self.headers)
        logger.debug(f"Control task response: {response.json()}")
        return response.json()

    def get_task_status(self, task_id):
        url = f"{self.base_url}/tasks/{task_id}"
        logger.debug(f"Getting task status with URL: {url}")
        response = requests.get(url, headers=self.headers)
        if response.status_code == 401:
            logger.warning("Access token expired, refreshing token.")
            self.refresh_access_token()
            response = requests.get(url, headers=self.headers)
        logger.debug(f"Task status response: {response.json()}")
        return response.json()

    async def get_task_updates(self, task_id):
        url = f"{self.base_url}/tasks/{task_id}/live_status"
        logger.debug(f"Getting task updates with URL: {url}")
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                if response.status == 401:
                    logger.warning("Access token expired, refreshing token.")
                    self.refresh_access_token()
                    async with session.get(url) as response:
                        async for update in self._handle_sse(response):
                            yield update
                else:
                    async for update in self._handle_sse(response):
                        yield update

    async def _handle_sse(self, response):
        logger.debug("Handling SSE")
        async for line in response.content:
            if line:
                line = line.decode('utf-8').strip()
                if line.startswith("data:"):
                    data = line.lstrip("data: ").strip()
                    logger.debug(f"Received SSE data: {data}")
                    yield data

    def list_tasks(self, page=1, limit=10):
        url = f"{self.base_url}/tasks"
        params = {
            'page': page,
            'limit': limit
        }
        logger.debug(f"Listing tasks with URL: {url} and params: {params}")
        response = requests.get(url, params=params, headers=self.headers)
        if response.status_code == 401:
            logger.warning("Access token expired, refreshing token.")
            self.refresh_access_token()
            response = requests.get(url, params=params, headers=self.headers)
        logger.debug(f"List tasks response: {response.json()}")
        return response.json()

    def register_webhook(self, webhook_data):
        url = f"{self.base_url}/tasks/webhooks"
        logger.debug(f"Registering webhook with URL: {url} and webhook_data: {webhook_data}")
        response = requests.post(url, json=webhook_data, headers=self.headers)
        if response.status_code == 401:
            logger.warning("Access token expired, refreshing token.")
            self.refresh_access_token()
            response = requests.post(url, json=webhook_data, headers=self.headers)
        logger.debug(f"Register webhook response: {response.json()}")
        return response.json()

    def get_profile(self):
        url = f"{self.base_url}/profile"
        logger.debug(f"Getting profile with URL: {url}")
        response = requests.get(url, headers=self.headers)
        if response.status_code == 401:
            logger.warning("Access token expired, refreshing token.")
            self.refresh_access_token()
            response = requests.get(url, headers=self.headers)
        logger.debug(f"Profile response: {response.json()}")
        return response.json()

    def change_password(self, old_password, new_password):
        url = f"{self.base_url}/profile/change_password"
        payload = {"old_password": old_password, "new_password": new_password}
        logger.debug(f"Changing password with URL: {url} and payload: {payload}")
        response = requests.post(url, json=payload, headers=self.headers)
        if response.status_code == 401:
            logger.warning("Access token expired, refreshing token.")
            self.refresh_access_token()
            response = requests.post(url, json=payload, headers=self.headers)
        logger.debug(f"Change password response: {response.json()}")
        return response.json()