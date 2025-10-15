#!/usr/bin/env python3
"""
Script to query Jira for tickets assigned to the current user.
Targets DI and CCS boards/projects on Jira.
"""
import configparser
import sys
from jira import JIRA


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


def get_current_user_email(jira):
    """Get the email of the currently authenticated user."""
    try:
        myself = jira.myself()
        return myself['emailAddress']
    except Exception as e:
        print(f"Error getting current user: {e}")
        return None


def get_my_tickets(jira, project_key, board_id=None):
    """
    Get tickets assigned to the current user from a specific project.
    
    Args:
        jira: JIRA client instance
        project_key: Project key (e.g., 'DI', 'CCS')
        board_id: Optional board ID for reference
    
    Returns:
        List of tickets assigned to current user
    """
    # JQL query to find tickets assigned to current user
    jql = f'project = {project_key} AND assignee = currentUser() ORDER BY updated DESC'
    
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
        'priority': issue.fields.priority.name if issue.fields.priority else 'None',
        'created': issue.fields.created,
        'updated': issue.fields.updated,
        'reporter': issue.fields.reporter.displayName if issue.fields.reporter else 'Unknown'
    }


def main():
    """Main function to query and display tickets assigned to current user."""
    print("=" * 80)
    print("My Assigned Tickets Report")
    print("=" * 80)
    print()
    
    # Load configuration and connect to Jira
    config = load_config()
    jira = connect_to_jira(config)
    
    # Get current user info
    user_email = get_current_user_email(jira)
    if user_email:
        print(f"Logged in as: {user_email}\n")
    
    # Define boards/projects to check
    boards = [
        {'project': 'DI', 'board_id': 705, 'name': 'DI Board'},
        {'project': 'CCS', 'board_id': None, 'name': 'CCS Project'}
    ]
    
    total_tickets = 0
    
    for board in boards:
        board_ref = f"Board ID: {board['board_id']}" if board['board_id'] else "Project"
        print(f"\nChecking {board['name']} (Project: {board['project']}, {board_ref})")
        print("-" * 80)
        
        my_tickets = get_my_tickets(jira, board['project'], board['board_id'])
        
        if my_tickets:
            print(f"Found {len(my_tickets)} ticket(s) assigned to you:\n")
            
            for issue in my_tickets:
                info = format_ticket_info(issue)
                print(f"  Key:          {info['key']}")
                print(f"  Summary:      {info['summary']}")
                print(f"  Status:       {info['status']}")
                print(f"  Priority:     {info['priority']}")
                print(f"  Reporter:     {info['reporter']}")
                print(f"  Last Updated: {info['updated']}")
                print(f"  URL:          {config['server']}/browse/{info['key']}")
                print()
            
            total_tickets += len(my_tickets)
        else:
            print("No tickets assigned to you.\n")
    
    print("=" * 80)
    print(f"Total tickets assigned to you across all boards: {total_tickets}")
    print("=" * 80)


if __name__ == "__main__":
    main()
