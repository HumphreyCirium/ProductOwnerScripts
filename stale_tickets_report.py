#!/usr/bin/env python3
"""
Script to identify and report tickets with no status change in the last 3 months.
Targets FDA and FDP boards on Jira.
"""
import configparser
import sys
from datetime import datetime, timedelta
from jira import JIRA
from dateutil import parser as date_parser


def load_config():
    """Load Jira configuration from config.ini file."""
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    if 'jira' not in config:
        print("Error: config.ini file not found or missing [jira] section.")
        print("Please create config.ini based on config.ini.example")
        sys.exit(1)
    
    return config['jira']


def connect_to_jira(config):
    """Establish connection to Jira."""
    try:
        jira = JIRA(
            server=config['server'],
            basic_auth=(config['email'], config['api_token'])
        )
        return jira
    except Exception as e:
        print(f"Error connecting to Jira: {e}")
        sys.exit(1)


def get_stale_tickets(jira, project_key, board_id, months=3):
    """
    Get tickets from a project/board with no status change in the last N months.
    
    Args:
        jira: JIRA client instance
        project_key: Project key (e.g., 'FDA', 'FDP')
        board_id: Board ID for reference
        months: Number of months to check (default 3)
    
    Returns:
        List of stale tickets
    """
    cutoff_date = datetime.now() - timedelta(days=months * 30)
    cutoff_date_str = cutoff_date.strftime('%Y-%m-%d')
    
    # JQL query to find tickets with no status change in the last N months
    # statusCategoryChangedDate tracks when the status category last changed
    jql = f'project = {project_key} AND statusCategoryChangedDate <= "{cutoff_date_str}"'
    
    try:
        issues = jira.search_issues(jql, maxResults=1000)
        return issues
    except Exception as e:
        print(f"Error searching for issues in {project_key}: {e}")
        return []


def format_ticket_info(issue):
    """Format ticket information for display."""
    return {
        'key': issue.key,
        'summary': issue.fields.summary,
        'status': issue.fields.status.name,
        'assignee': issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned',
        'created': issue.fields.created,
        'updated': issue.fields.updated,
        'status_changed': getattr(issue.fields, 'statuscategorychangedate', 'N/A')
    }


def main():
    """Main function to identify and report stale tickets."""
    print("=" * 80)
    print("Stale Tickets Report - No Status Change in Last 3 Months")
    print("=" * 80)
    print()
    
    # Load configuration and connect to Jira
    config = load_config()
    jira = connect_to_jira(config)
    
    # Define boards to check
    boards = [
        {'project': 'FDA', 'board_id': 740, 'name': 'FDA Board'},
        {'project': 'FDP', 'board_id': 728, 'name': 'FDP Board'}
    ]
    
    total_stale = 0
    
    for board in boards:
        print(f"\nChecking {board['name']} (Project: {board['project']}, Board ID: {board['board_id']})")
        print("-" * 80)
        
        stale_tickets = get_stale_tickets(jira, board['project'], board['board_id'])
        
        if stale_tickets:
            print(f"Found {len(stale_tickets)} stale ticket(s):\n")
            
            for issue in stale_tickets:
                info = format_ticket_info(issue)
                print(f"  Key:            {info['key']}")
                print(f"  Summary:        {info['summary']}")
                print(f"  Status:         {info['status']}")
                print(f"  Assignee:       {info['assignee']}")
                print(f"  Last Updated:   {info['updated']}")
                print(f"  Status Changed: {info['status_changed']}")
                print(f"  URL:            {config['server']}/browse/{info['key']}")
                print()
            
            total_stale += len(stale_tickets)
        else:
            print("No stale tickets found.\n")
    
    print("=" * 80)
    print(f"Total stale tickets across all boards: {total_stale}")
    print("=" * 80)


if __name__ == "__main__":
    main()
