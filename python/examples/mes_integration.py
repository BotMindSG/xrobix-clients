"""
This script monitors a specified input file for changes in a number.
If the number changes to {start_task_number}, it starts a predefined task on the Xrobix Robot Management Platform API.
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
- Run the script: `python mes_integration.py`
"""

import sys
import os
import json
import time
import threading
import asyncio
import logging
# Add the parent directory to the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from xrobix_client import XRobixClient

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# TODO: obtain the following information from Botmind team
base_url = "https://dev.xrobix.com/api/v1"
username = "{INSERT YOUR USERNAME}"
password = "{INSERT YOUR PASSWORD}"
task_id = "{INSERT YOUR TASK_ID}"

# TODO: update according to your own logic
input_file_path = "input_number.txt"
output_file_path = "output_number.txt"
start_task_number = 1
end_task_number = 2

# Function to read a number from a file
def read_number_from_file(file_path):
    logger.debug(f"Reading number from file: {file_path}")
    with open(file_path, 'r') as file:
        number = int(file.read().strip())
    logger.debug(f"Read number: {number}")
    return number

# Function to write a number to a file
def write_number_to_file(file_path, number):
    logger.debug(f"Writing number {number} to file: {file_path}")
    with open(file_path, 'w') as file:
        file.write(str(number))
    logger.debug(f"Number written to file: {file_path}")

# Asynchronous function to listen for task updates using aiohttp
async def listen_for_task_updates(client: XRobixClient, task_id, output_file_path):
    async for update in client.get_task_updates(task_id):
        update_data = json.loads(update)
        logger.debug(f"Task Update: {update_data}")

        # Check if the task status is completed
        if update_data.get("status") == "completed":
            logger.info("Task completed.")

            # Write the end_task_number to the output file
            write_number_to_file(output_file_path, end_task_number)

            # Stop tracking the task updates
            break

# Function to process tasks based on the input number
def process_tasks(client: XRobixClient, input_file_path, output_file_path):
    last_number = None
    while True:
        number = read_number_from_file(input_file_path)
        # NOTE: if the number inside input_file is updated by MES
        if number != last_number:
            last_number = number
            # NOTE: the task request will be sent if the number matches start_task_number
            if number == start_task_number:
                logger.info(f"Starting task with ID: {task_id}")

                # Start the task
                control_response = client.control_task(task_id, "start")
                logger.debug(f"Task {task_id} started: {control_response}")

                # Call get_task_updates API and listen for updates
                asyncio.run(listen_for_task_updates(client, task_id, output_file_path))
        time.sleep(1)  # Check for changes every second

# Main function to handle the task workflow
def main():
    client = XRobixClient(base_url, username, password)

    # Start processing tasks based on the input number
    process_tasks_thread = threading.Thread(target=process_tasks, args=(client, input_file_path, output_file_path))
    process_tasks_thread.start()

if __name__ == "__main__":
    main()