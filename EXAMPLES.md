# Usage Examples

## Initial Setup
```bash
# Clone the repository
git clone https://github.com/HumphreyCirium/ProductOwnerScripts.git
cd ProductOwnerScripts

# Install dependencies
pip install -r requirements.txt

# Configure credentials
cp config.ini.example config.ini
# Edit config.ini with your Jira email and API token
```

## Running the Scripts

### Stale Tickets Report
```bash
python stale_tickets_report.py
```

**Example Output:**
```
================================================================================
Stale Tickets Report - No Status Change in Last 3 Months
================================================================================

Checking FDA Board (Project: FDA, Board ID: 740)
--------------------------------------------------------------------------------
Found 5 stale ticket(s):

  Key:            FDA-123
  Summary:        Update documentation for API endpoints
  Status:         In Progress
  Assignee:       John Doe
  Last Updated:   2023-04-15T10:30:00.000+0000
  Status Changed: 2023-01-20T14:45:00.000+0000
  URL:            https://cirium.atlassian.net/browse/FDA-123

  Key:            FDA-145
  Summary:        Fix login validation bug
  Status:         To Do
  Assignee:       Unassigned
  Last Updated:   2023-03-22T09:15:00.000+0000
  Status Changed: 2023-02-10T11:20:00.000+0000
  URL:            https://cirium.atlassian.net/browse/FDA-145

Checking FDP Board (Project: FDP, Board ID: 728)
--------------------------------------------------------------------------------
Found 3 stale ticket(s):

  Key:            FDP-89
  Summary:        Implement new caching strategy
  Status:         In Review
  Assignee:       Jane Smith
  Last Updated:   2023-05-01T16:00:00.000+0000
  Status Changed: 2023-01-15T13:30:00.000+0000
  URL:            https://cirium.atlassian.net/browse/FDP-89

================================================================================
Total stale tickets across all boards: 8
================================================================================
```

### My Tickets Report
```bash
python my_tickets_report.py
```

**Example Output:**
```
================================================================================
My Assigned Tickets Report
================================================================================

Logged in as: john.doe@cirium.com

Checking DI Board (Project: DI, Board ID: 705)
--------------------------------------------------------------------------------
Found 4 ticket(s) assigned to you:

  Key:          DI-234
  Summary:      Implement data validation for user input
  Status:       In Progress
  Priority:     High
  Reporter:     Jane Smith
  Last Updated: 2023-07-10T14:30:00.000+0000
  URL:          https://cirium.atlassian.net/browse/DI-234

  Key:          DI-256
  Summary:      Add unit tests for API endpoints
  Status:       To Do
  Priority:     Medium
  Reporter:     Bob Johnson
  Last Updated: 2023-07-08T09:15:00.000+0000
  URL:          https://cirium.atlassian.net/browse/DI-256

Checking CCS Project (Project: CCS, Project)
--------------------------------------------------------------------------------
Found 2 ticket(s) assigned to you:

  Key:          CCS-589
  Summary:      Review and update security policies
  Status:       In Review
  Priority:     Critical
  Reporter:     Alice Williams
  Last Updated: 2023-07-12T11:45:00.000+0000
  URL:          https://cirium.atlassian.net/browse/CCS-589

================================================================================
Total tickets assigned to you across all boards: 6
================================================================================
```

## Tips

### Filtering Results
The scripts query all tickets. You can modify the JQL queries in the scripts to add additional filters:
- Status: `AND status = "In Progress"`
- Priority: `AND priority = High`
- Labels: `AND labels = "urgent"`
- Date range: `AND created >= "2023-01-01"`

### Scheduling Reports
You can schedule these scripts to run automatically using cron (Linux/Mac) or Task Scheduler (Windows):

**Linux/Mac cron example (daily at 9 AM):**
```bash
0 9 * * * cd /path/to/ProductOwnerScripts && python stale_tickets_report.py > /tmp/stale_tickets_$(date +\%Y\%m\%d).txt 2>&1
```

### Exporting to CSV
To save results to a file for later analysis:
```bash
python stale_tickets_report.py > stale_tickets_report.txt
python my_tickets_report.py > my_tickets_report.txt
```

## Troubleshooting

### Authentication Errors
```
Error connecting to Jira: HTTP 401: Unauthorized
```
**Solution:** Check that your API token is valid and hasn't expired. Generate a new one if needed.

### Permission Errors
```
Error searching for issues in FDA: You do not have permission to view this project
```
**Solution:** Ensure you have access to the specified project/board in Jira. Contact your Jira administrator if needed.

### Network Errors
```
Error connecting to Jira: Connection timeout
```
**Solution:** Check your network connection and ensure you can access https://cirium.atlassian.net in your browser.
