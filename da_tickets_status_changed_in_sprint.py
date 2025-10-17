import sys
import requests
import configparser
import csv
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta

def load_config():
    """Load Jira configuration from config.ini file."""
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    if 'jira' not in config:
        print("Error: config.ini file not found or missing [jira] section.")
        print("Please create config.ini based on config.ini.example")
        sys.exit(1)
    
    return config['jira']

def main():
    # Load configuration
    jira_config = load_config()

    # Extract credentials and settings from config
    JIRA_DOMAIN = jira_config.get("server")
    JIRA_EMAIL = jira_config.get("email")
    JIRA_API_TOKEN = jira_config.get("api_token")
    JIRA_BOARD_NAME = jira_config.get("board_name")

    # Jira API endpoint to search issues
    url = f"{JIRA_DOMAIN}/rest/api/3/search/jql"

    # Calculate date one sprint ago
    one_sprint_ago = (datetime.today() - timedelta(days=27)).strftime('%Y-%m-%d')

    # JQL query to find issues with status changes after one sprint ago
    jql_query = f'project = "{JIRA_BOARD_NAME}" AND (status changed AFTER "{one_sprint_ago}")'

    # Request headers and parameters
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    params = {
        "jql": jql_query,
        "fields": "summary,status"
    }

    # Make the request to Jira API
    response = requests.get(
        url,
        headers=headers,
        params=params,
        auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
    )

# Check if the request was successful
if response.status_code == 200:
    issues = response.json().get("issues", [])
    for issue in issues:
        issue_id = issue["key"]
        summary = issue["fields"]["summary"]
        status = issue["fields"]["status"]["name"]
        print(f"ID: {issue_id}, Summary: {summary}, Status: {status}")
else:
    print(f"Failed to retrieve issues: {response.status_code} - {response.text}")
    
    
if response.status_code == 200:
    issues = response.json().get("issues", [])
    with open("C:\\Users\\pasleyh\\OneDrive - Reed Elsevier Group ICO Reed Elsevier Inc\\Documents\\Scripts\\da status change.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Summary", "Status"])
        for issue in issues:
            issue_id = issue["key"]
            summary = issue["fields"]["summary"]
            status = issue["fields"]["status"]["name"]
            writer.writerow([issue_id, summary, status])
    print("Issues exported to active da status change.csv")
else:
    print(f"Failed to retrieve issues: {response.status_code} - {response.text}")

if __name__ == "__main__":
    main()