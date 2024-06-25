from xrobix_client import XRobixClient

# Initialize client
client = XRobixClient(base_url="https://dev.xrobix.com/v1", username="your_username", password="your_password")

# Submit a task
task_data = {
    "name": "Sample Task",
    "description": "This is a sample task",
    "robot_ids": ["robot_1"],
    "schedule": {
        "time": "2024-07-01T10:00:00Z",
        "repeat": "none"
    },
    "actions": [
        {
            "type": "navigate_to",
            "parameters": {
                "destination_marker": "A1",
                "speed": 1.5
            }
        }
    ]
}
response = client.submit_task(task_data)
print(response)
