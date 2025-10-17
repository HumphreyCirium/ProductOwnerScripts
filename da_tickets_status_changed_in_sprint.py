import requests
import datetime
import csv
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta

# Replace with your actual Jira credentials and domain
JIRA_DOMAIN = "https://cirium.atlassian.net"
JIRA_EMAIL = "humphrey.pasley@cirium.com"
JIRA_BOARD_NAME = "FDA"

# Jira API endpoint to search issues
url = f"{JIRA_DOMAIN}/rest/api/3/search/jql"

# JQL query to find issues assigned to the current user on the CCS board
#jql_query = f'project = "{JIRA_BOARD_NAME}" AND assignee = currentUser()'

one_sprint_ago = (datetime.today() - timedelta(days=27)).strftime('%Y-%m-%d')

# JQL query to find issues assigned to the current user on the CCS board
# and exclude 'Done' issues that haven't had a status change in the last month
jql_query = (
    f'project = "{JIRA_BOARD_NAME}" AND (status changed AFTER "{one_sprint_ago}")'

)

# Request headers
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# Request parameters
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

