# ProductOwnerScripts
A set of scripts for carrying out Product Owner tasks

## Overview
This repository contains Python scripts to automate common Product Owner tasks in Jira, including:
- Identifying stale tickets (no status change in last 3 months)
- Querying tickets assigned to you

## Prerequisites
- Python 3.7 or higher
- Jira API token (see setup instructions below)

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Jira Credentials
Create a `config.ini` file based on the example:
```bash
cp config.ini.example config.ini
```

Edit `config.ini` with your Jira credentials:
```ini
[jira]
server = https://cirium.atlassian.net
email = your-email@cirium.com
api_token = your-api-token-here
```

### 3. Generate Jira API Token
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a name (e.g., "ProductOwnerScripts")
4. Copy the token and paste it into `config.ini`

## Scripts

### stale_tickets_report.py
Identifies and reports tickets with no status change in the last 3 months.

**Boards checked:**
- FDA Board (https://cirium.atlassian.net/jira/software/c/projects/FDA/boards/740)
- FDP Board (https://cirium.atlassian.net/jira/software/c/projects/FDP/boards/728)

**Usage:**
```bash
python stale_tickets_report.py
```

**Output:**
- List of all tickets with no status change in the last 3 months
- Ticket details: Key, Summary, Status, Assignee, Last Updated, Status Changed Date
- Direct links to each ticket

### my_tickets_report.py
Queries and displays tickets assigned to you.

**Boards/Projects checked:**
- DI Board (https://cirium.atlassian.net/jira/software/c/projects/DI/boards/705)
- CCS Project (https://cirium.atlassian.net/browse/CCS)

**Usage:**
```bash
python my_tickets_report.py
```

**Output:**
- List of all tickets currently assigned to you
- Ticket details: Key, Summary, Status, Priority, Reporter, Last Updated
- Direct links to each ticket

## Security Note
**Never commit your `config.ini` file!** It contains your API token which should be kept secret. The `.gitignore` file is configured to exclude this file.

## Troubleshooting

### Connection Issues
- Verify your API token is valid
- Check that your email address is correct
- Ensure you have network access to Jira

### No Results
- Verify you have access to the specified projects/boards
- Check that the project keys are correct (FDA, FDP, DI, CCS)

## License
MIT License
