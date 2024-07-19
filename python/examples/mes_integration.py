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
from functools import partial
from dotenv import load_dotenv

# Add the parent directory to the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from xrobix_client import XRobixClient

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Load configuration from environment variables
base_url = os.getenv("BASE_URL")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

# TODO: Initialize the task map
task_map = {
    1: "eebe62d0-cfab-4845-8b3a-2d15de0504cc",
    2: "{TASK_ID_2}",
    3: "{TASK_ID_3}",
    4: "{TASK_ID_4}"
    # Add more task_number: task_id pairs as needed
}

# TODO: update according to your own computer setup
input_file_path = "input_number.txt"
output_file_path = "output_number.txt"

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
async def listen_for_task_updates(client: XRobixClient, task_id, task_map, output_file_path):
    async for update in client.get_task_updates(task_id):
        update_data = json.loads(update)
        logger.debug(f"Task Update: {update_data}")

        # Check if the task status is completed
        if update_data.get("status") == "completed":
            logger.info("Task completed.")
            task_id = update_data.get("id")
            # Obtain task_number from task_id using the task_map
            task_number = next(key for key, value in task_map.items() if value == task_id)
            # Write the end_task_number to the output file
            write_number_to_file(output_file_path, task_number)

            # Stop tracking the task updates
            break

# Function to process tasks based on the input number
def process_tasks(loop, client, input_file_path, output_file_path, task_map):
    last_number = None
    while True:
        number = read_number_from_file(input_file_path)
        # Check if the number inside input_file is updated by MES
        if number != last_number:
            last_number = number
            # Check if the number matches a task_number in the task_map
            if number in task_map:
                task_id = task_map[number]
                logger.info(f"Starting task with ID: {task_id}")

                # Start the task
                control_response = client.control_task(task_id, "start")
                logger.debug(f"Task {task_id} started: {control_response}")

                # Call get_task_updates API and listen for updates
                asyncio.run_coroutine_threadsafe(
                    listen_for_task_updates(client, task_id, task_map, output_file_path),
                    loop
                )
        time.sleep(1)  # Check for changes every second

# Main function to handle the task workflow
def main():
    # Initialize the output file with 0
    write_number_to_file(output_file_path, 0)
    
    client = XRobixClient(base_url, username, password)

    # Create a new event loop for the main thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Start processing tasks based on the input number in a separate thread
    process_tasks_thread = threading.Thread(target=process_tasks, args=(loop, client, input_file_path, output_file_path, task_map))
    process_tasks_thread.start()

    # Run the event loop in the main thread
    loop.run_forever()

if __name__ == "__main__":
    main()