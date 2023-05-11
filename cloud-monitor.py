import json
import logging
import threading
import time
import yaml
import requests
from pymongo import MongoClient

# Configure the logging system
sys_logger = logging.getLogger(__name__)
sys_logger.setLevel(logging.DEBUG)

try:
    # Connect to the MongoDB server
    client = MongoClient('mongodb://mongo:27017/')

    # Get the database and collection
    db = client['mydatabase']
    collection = db['mycollection']

# Logs the error message and exception details when failing to connect to the database
# Should send these errors directly to support staff, wont be able to log to database seeing that the database can't be connected to
except Exception as e:
    sys_logger.error("Error: Could not connect to MongoDB server.", exc_info=True)

# Creates a handler that sends log messages to the log_database
class MongoDBHandler(logging.Handler):
    def emit(self, record):
        log_entry = {
            'timestamp' : record.created,
            'level' : record.levelname,
            'message' : self.format(record),
            'source' : record.name
        }
        collection.insert_one(log_entry)

handler = MongoDBHandler()
handler.setLevel(logging.INFO)

# Adds the handler to the logger
sys_logger.addHandler(handler)


def get_status_and_response_time(hostname):
    """
    Get the status code and response time of a GET request to the specified hostname.

    :param hostname: The hostname to send the GET request to.
    :type hostname: str
    :return: A tuple containing the status code and response time in milliseconds, or (None, None) if an error occurred.
    :rtype: tuple
    """
    try:
        r = requests.get(hostname)
        return r.status_code, int(r.elapsed.total_seconds() * 1000)
    except requests.exceptions.RequestException as e:
        sys_logger.error(f'An error occurred while getting the status and response time of {hostname}: {e}')
        return None, None

def send_discord_message(webhook_url, content):
    """
    Send a message to a Discord channel using a webhook.

    :param webhook_url: The URL of the Discord webhook.
    :type webhook_url: str
    :param content: The content of the message to send.
    :type content: str
    """
    headers = {'Content-Type': 'application/json'}
    data = {'content': content}
    try:
        requests.post(webhook_url, headers=headers, data=json.dumps(data))
    except requests.exceptions.RequestException as e:
        sys_logger.error(f'An error occurred while sending a Discord message: {e}')

def ping_service(service):
    """
    Continuously ping a service and log its status and response time.

    :param service: A dictionary containing information about the service to ping.
    :type service: dict
    """
    while True:
        hostname = service['hostname']
        status_code, response_time = get_status_and_response_time(hostname)
        log_data = {
            'hostname': hostname,
            'timestamp': int(time.time()),
            'status_code': status_code,
            'response_time': response_time
        }
        if status_code is None:
            send_discord_message(service['discord'], f'{hostname} is down!')
            sys_logger.warning(f'{hostname} is down!')
            log_data['status'] = 'down'
        else:
            sys_logger.info(f'{hostname} is up! Status code: {status_code}, response time: {response_time} ms')
            log_data['status'] = 'up'
        collection.insert_one(log_data)
        time.sleep(service['time'])

def main():
    """
    Load service information from a YAML file and start a thread for each service to ping it continuously.
    """
    with open('data.yaml') as f:
        my_list = yaml.safe_load(f)
        for key in my_list:
            service = key['services']
            t = threading.Thread(target=ping_service, args=(service,))
            t.start()

if __name__ == '__main__':
    main()
