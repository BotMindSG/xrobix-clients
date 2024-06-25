"""
This script monitors a specified input file for changes in a number.
If the number changes to {start_task_number}, it submits a predefined task to the Xrobix Robot Management Platform API.
The script then listens for updates on the task status.
When the task is completed, it writes the {end_task_number} to a specified output file.

Functions:
- read_number_from_file(file_path): Reads a number from a text file.
- write_number_to_file(file_path, number): Writes a number to a text file.
- listen_for_task_updates(client, task_id, output_file_path): Listens for task updates and writes to the output file when the task is completed.
- process_tasks(client, input_file_path, output_file_path): Monitors the input file for changes and processes tasks accordingly.
- main(): Initializes the XrobixClient and starts the task processing thread.

Usage:
- Update the `base_url`, `username`, and `password` variables with your Xrobix API credentials.
- Ensure `input_number.txt` contains an initial number
- Run the script: `python example_task_workflow.py`
"""

import json
import time
import threading
from xrobix_client import XRobixClient


# TODO: obtain the following information from Botmind team
base_url = "https://dev.xrobix.com/v1"
username = "your_username_here"
password = "your_password_here"
robot_id = "your_robot_id_here"

# TODO: update according to your own logic
input_file_path = "input_number.txt"
output_file_path = "output_number.txt"
start_task_number = 1
end_task_number = 2


# Function to read a number from a file
def read_number_from_file(file_path):
    with open(file_path, 'r') as file:
        number = int(file.read().strip())
    return number

# Function to write a number to a file
def write_number_to_file(file_path, number):
    with open(file_path, 'w') as file:
        file.write(str(number))

# Function to listen for task updates
def listen_for_task_updates(client, task_id, output_file_path):
    for update in client.get_task_updates(task_id):
        update_data = json.loads(update)
        print(f"Task Update: {update_data}")

        # Check if the task is completed
        if update_data.get("task_status") == "completed":
            print("Task completed.")

            # NOTE: Write the end_task_number to the output file
            write_number_to_file(output_file_path, end_task_number)

            # Stop tracking the task updates
            break

# Function to process tasks based on the input number
def process_tasks(client, input_file_path, output_file_path):
    last_number = None
    while True:
        number = read_number_from_file(input_file_path)
        # NOTE: if the number inside input_file is updated by MES
        if number != last_number:
            last_number = number
            # NOTE: the task request will be send if the number matches start_task_number
            if number == start_task_number:
                # Define the task data template
                task_data = {
                    "robot_ids": [robot_id],
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

                # Submit the task
                response = client.submit_task(task_data)
                task_id = response.get("task_id")
                print(f"Task submitted with ID: {task_id}")

                # Call get_task_updates API and listen for updates in a separate thread
                if task_id:
                    update_thread = threading.Thread(target=listen_for_task_updates, args=(client, task_id, output_file_path))
                    update_thread.start()
        time.sleep(1)  # Check for changes every second

# Main function to handle the task workflow
def main():
    client = XRobixClient(base_url, username, password)

    input_file_path = "input_number.txt"
    output_file_path = "output_number.txt"

    # Start processing tasks based on the input number
    process_tasks_thread = threading.Thread(target=process_tasks, args=(client, input_file_path, output_file_path))
    process_tasks_thread.start()

if __name__ == "__main__":
    main()
