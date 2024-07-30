import os
import json
import glob
import hashlib
from datadog import initialize, api

options = {
    'api_key': os.getenv('DATADOG_API_KEY'),
    'app_key': os.getenv('DATADOG_APP_KEY'),
    'api_host': 'https://api.us5.datadoghq.com'
}

initialize(**options)

# Function to compute the checksum of a file
def compute_checksum(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def create_or_update_dashboard(file_path, dashboard_data):
    existing_dashboards = api.Dashboard.get_all()
    
    # Check if a dashboard with the same title exists
    existing_dashboard = None
    for dashboard in existing_dashboards['dashboards']:
        if dashboard['title'] == dashboard_data['title']:
            existing_dashboard = dashboard
            break
    
    if existing_dashboard:
        # Update existing dashboard if content has changed
        dashboard_id = existing_dashboard['id']
        existing_dashboard_data = api.Dashboard.get(dashboard_id)
        
        if existing_dashboard_data['widgets'] != dashboard_data['widgets']:
            response = api.Dashboard.update(dashboard_id, **dashboard_data)
            print(f"Dashboard updated for {file_path}: {response}")
        else:
            print(f"No changes detected for {file_path}, skipping update.")
    else:
        response = api.Dashboard.create(**dashboard_data)
        print(f"Dashboard created for {file_path}: {response}")

# Load previous checksums from file
checksums_file = 'checksums.json'
if os.path.exists(checksums_file):
    with open(checksums_file, 'r') as file:
        previous_checksums = json.load(file)
else:
    previous_checksums = {}

# Find and process all dashboard.json files
dashboard_files = glob.glob('**/dashboard.json')
current_checksums = {}

for file_path in dashboard_files:
    checksum = compute_checksum(file_path)
    current_checksums[file_path] = checksum

    if previous_checksums.get(file_path) != checksum:
        print(f'Processing {file_path}')
        with open(file_path, 'r') as file:
            dashboard_data = json.load(file)
        create_or_update_dashboard(file_path, dashboard_data)
    else:
        print(f'Skipping {file_path}, no changes detected.')

# Save current checksums to file
with open(checksums_file, 'w') as file:
    json.dump(current_checksums, file)