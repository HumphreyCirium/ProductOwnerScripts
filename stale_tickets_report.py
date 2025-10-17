#!/usr/bin/env python3
"""
Script to identify and report tickets with no status change in the last 3 months.
Targets FDA and FDP boards on Jira.
"""
import configparser
import sys
from datetime import datetime, timedelta
import requests
import csv
from requests.auth import HTTPBasicAuth


def load_config():
    """Load Jira configuration from config.ini file."""
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    if 'jira' not in config:
        print("Error: config.ini file not found or missing [jira] section.")
        print("Please create config.ini based on config.ini.example")
        sys.exit(1)
    
    return config['jira']


def get_stale_tickets(config, project_key, months=3):
    """
    Get tickets from a project with no status change in the last N months.
    
    Args:
        config: Configuration dictionary with Jira credentials
        project_key: Project key (e.g., 'FDA', 'FDP')
        months: Number of months to check (default 3)
    
    Returns:
        List of stale tickets
    """
    cutoff_date = datetime.now() - timedelta(days=months * 30)
    cutoff_date_str = cutoff_date.strftime('%Y-%m-%d')
    
    # Jira API endpoint to search issues
    url = f"{config['server']}/rest/api/3/search/jql/"
    
    # JQL query to find tickets with no status change in the last N months
    jql_query = f'project = {project_key} AND status changed BEFORE "{cutoff_date_str}" AND (updated >= "{cutoff_date_str}" OR created >= "{cutoff_date_str}")'
    
    # Alternative query if the above doesn't work as expected:
    # This finds tickets that either:
    # 1. Haven't changed status since before the cutoff date
    # 2. Are still in an active status (not Done/Closed)
    # You might need to adjust based on your Jira setup
  #  jql_query = f'project = {project_key} AND (statusCategoryChangedDate <= "{cutoff_date_str}" OR statusCategoryChangedDate is EMPTY) AND status != Done AND status != Closed'
    
    # Request headers
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # Request parameters
    params = {
        "jql": jql_query,
        "fields": "summary,status,assignee,created,updated,statuscategorychangedate",
        "maxResults": 1000
    }
    
    try:
        # Make the request to Jira API
        response = requests.get(
            url,
            headers=headers,
            params=params,
            auth=HTTPBasicAuth(config['email'], config['api_token'])
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('issues', [])
        else:
            print(f"Error searching for issues in {project_key}: {response.status_code}")
            print(f"Response: {response.text}")
            return []
    except Exception as e:
        print(f"Error searching for issues in {project_key}: {e}")
        return []


def format_ticket_info(issue, server):
    """Format ticket information for display."""
    fields = issue.get('fields', {})
    assignee = fields.get('assignee')
    status = fields.get('status', {})
    
    return {
        'key': issue.get('key', 'N/A'),
        'summary': fields.get('summary', 'N/A'),
        'status': status.get('name', 'N/A') if status else 'N/A',
        'assignee': assignee.get('displayName', 'Unassigned') if assignee else 'Unassigned',
        'created': fields.get('created', 'N/A'),
        'updated': fields.get('updated', 'N/A'),
        'status_changed': fields.get('statuscategorychangedate', 'N/A'),
        'url': f"{server}/browse/{issue.get('key', '')}"
    }


def main():
    """Main function to identify and report stale tickets."""
    print("=" * 80)
    print("Stale Tickets Report - No Status Change in Last 3 Months")
    print("=" * 80)
    print()
    
    # Load configuration
    config = load_config()
    
    # Define boards/projects to check
    boards = [
        {'project': 'FDA', 'board_id': 740, 'name': 'FDA Board'},
        {'project': 'FDP', 'board_id': 728, 'name': 'FDP Board'}
    ]
    
    total_stale = 0
    
    for board in boards:
        print(f"\nChecking {board['name']} (Project: {board['project']}, Board ID: {board['board_id']})")
        print("-" * 80)
        
        stale_tickets = get_stale_tickets(config, board['project'])
        
        if stale_tickets:
            print(f"Found {len(stale_tickets)} stale ticket(s):\n")
            
            for issue in stale_tickets:
                info = format_ticket_info(issue, config['server'])
                print(f"  Key:            {info['key']}")
                print(f"  Summary:        {info['summary']}")
                print(f"  Status:         {info['status']}")
                print(f"  Assignee:       {info['assignee']}")
                print(f"  Last Updated:   {info['updated']}")
                print(f"  Status Changed: {info['status_changed']}")
                print(f"  URL:            {info['url']}")
                print()
            
            total_stale += len(stale_tickets)
        else:
            print("No stale tickets found.\n")

        # Export issues to CSV
        output_path = "C:\\Users\\pasleyh\\OneDrive - Reed Elsevier Group ICO Reed Elsevier Inc\\Documents\\Scripts\\Stale Tickets Report.csv"
        with open(output_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Summary", "Status"])
            for issue in stale_tickets:
                info = format_ticket_info(issue, config['server'])                
                issue_id = info['key']
                summary = info['summary']
                status = info['status']
                updated = info['updated']

                writer.writerow([issue_id, summary, status,updated])
        print("Issues exported to Stale Tickets Report.csv")
    
    print("=" * 80)
    print(f"Total stale tickets across all boards: {total_stale}")
    print("=" * 80)


if __name__ == "__main__":
    main()