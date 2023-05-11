# cloud-monitor.py #
This Python script is designed to continuously monitor specified services and log their status and response time. It also includes functionality to send a message to a Discord channel if a service is down.

### Dependencies ###
This script has the following dependencies:

json
logging
threading
time
yaml
requests
pymongo

### Configuration ###
Before running the script, you need to configure the following:

A MongoDB server and its connection details.
The names of your MongoDB database and collection.
A Discord webhook URL (optional).
Service information in a YAML file.
How to Run
Install the dependencies listed above.
Configure the necessary parameters.
Run the Python script.

# query.py #
This Python script generates two plots of data from a MongoDB collection for a specific hostname and sends them to the corresponding Discord webhook specified in a data.yaml file.

### Dependencies ###
This script requires the following Python packages:

logging
yaml
pymongo
pandas
matplotlib
requests
io
time

These can be installed via pip if not already installed.

### Usage ###
Ensure that a MongoDB instance is running at mongodb://mongo:27017/ with a database called mydatabase and a collection called mycollection.
Create a data.yaml file with the following schema:
- services:
    hostname: [hostname]
    discord: [webhook_url]


where [hostname] is the hostname to generate plots for and [webhook_url] is the Discord webhook URL to send the plots to. You can specify multiple services in the YAML file to generate plots for multiple hosts. 3. Execute the script using python monitoring_plot_generator.py. It will generate a plot for each hostname specified in data.yaml every 60 seconds and send them to the corresponding Discord webhooks. The script will run indefinitely until manually interrupted. 4. The script will generate two plots for each hostname: one for response time and one for status codes. The plots will be saved as plot.png and sent as file attachments to the Discord webhooks.