import os
import json
import glob
from datadog import initialize, api

# Initialize Datadog
options = {
    'api_key': os.getenv('DATADOG_API_KEY'),
    'app_key': os.getenv('DATADOG_APP_KEY'),
    'api_host': 'https://api.us5.datadoghq.com'
}

initialize(**options)

def create_dashboard(file_path):
    try:
        with open(file_path, 'r') as file:
            dashboard_data = json.load(file)
        print(f'Dashboard data for {file_path}:', json.dumps(dashboard_data, indent=2))
        response = api.Dashboard.create(**dashboard_data)
        if 'errors' in response:
            print(f'Error creating dashboard for {file_path}:', response['errors'])
        else:
            print(f'Dashboard created for {file_path}:', response)
    except Exception as e:
        print(f'Exception occurred while processing {file_path}:', str(e))

# Find and process all dashboard.json files
for file_path in glob.glob('client2/dashboard.json'):
    print(f'Processing {file_path}')
    create_dashboard(file_path)
