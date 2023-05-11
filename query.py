import logging
import yaml
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import requests
from io import BytesIO
import time

# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO)

def send_discord_message(webhook_url, file):
    """
    Sends a Discord message with an attached file to the specified webhook URL.

    :param webhook_url: The webhook URL to send the message to.
    :param file: The file to attach to the message.
    """
    files = {'file': ('plot.png', file, 'image/png')}
    try:
        requests.post(webhook_url, files=files)
    except requests.exceptions.RequestException as e:
        logging.error(f'An error occurred while sending a Discord message: {e}')

def generate_plot(hostname):
    """
    Generates two plots of data from a MongoDB collection for a specific hostname and sends them to the corresponding Discord webhook specified in a data.yaml file.

    :param hostname: The hostname to generate the plots for.
    """
    # Clear the current figure
    plt.clf()

    # Connect to the MongoDB server and retrieve the data
    client = MongoClient('mongodb://mongo:27017/')
    db = client['mydatabase']
    collection = db['mycollection']
    data = list(collection.find({'hostname': hostname}))
    logging.info(f'Data for {hostname}: {data}')
    df = pd.DataFrame(data)

    # Generate the first plot (response time)
    plt.plot(df['response_time'])
    plt.title(f'Response Time for {hostname}')
    plt.xlabel('Index')
    plt.ylabel('Response Time (ms)')
    
    # Save the first plot to a buffer
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Clear the current figure
    plt.clf()

    # Generate the second plot (status codes)
    status_counts = df['status_code'].value_counts()
    status_counts.plot(kind='bar', stacked=True)
    plt.title(f'Status Codes for {hostname}')
    plt.xlabel('Status Code')
    plt.ylabel('Count')
    
    # Save the second plot to a buffer
    buf2 = BytesIO()
    plt.savefig(buf2, format='png')
    buf2.seek(0)

    # Load the data from the data.yaml file and send the plots to the corresponding webhook URL
    with open('data.yaml') as f:
        data = yaml.safe_load(f)
        for service in data:
            if service['services']['hostname'] == hostname:
                # Send the first plot (response time)
                webhook_url = service['services']['discord']
                send_discord_message(webhook_url, buf.read())
                
                # Send the second plot (status codes)
                webhook_url = service['services']['discord']
                send_discord_message(webhook_url, buf2.read())

def main():
    """
    Main function that generates a plot for each hostname every 60 seconds.
    """
    
    # Add a delay of 60 seconds before sending the first message
    time.sleep(60)

    # Send a message every 60 seconds
    while True:
        with open('data.yaml') as f:
            data = yaml.safe_load(f)
            for service in data:
                hostname = service['services']['hostname']
                logging.info(f'Generating plot for {hostname}')
                generate_plot(hostname)
        
        # Wait for 60 seconds before sending the next message
        time.sleep(3600)

if __name__ == '__main__':
    main()