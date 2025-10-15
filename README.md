# ProductOwnerScripts
A set of scripts for carrying out Product Owner tasks

## Tempo Timesheet Analyzer

Analyze Tempo timesheet data and generate comprehensive reports summarizing logged hours by account code, ticket, and team member.

### Features

- 🔐 **Authentication**: Supports API tokens for both Jira and Tempo APIs
- 📊 **Comprehensive Reports**: Generates detailed and summary reports in CSV or Excel format
- 🔧 **Configurable Parameters**: Supports date ranges, user filtering, and custom output options
- 📈 **Multiple Views**: 
  - Detailed worklog entries
  - Summary by team member, account code, and ticket
  - Team member totals
- 🎯 **Flexible Configuration**: Use config files or environment variables
- 📤 **Export Options**: CSV (multiple files) or Excel (multiple sheets)

### Prerequisites

- Python 3.7 or higher
- Jira instance with Tempo timesheets enabled
- API tokens:
  - Jira API token (from https://id.atlassian.com/manage-profile/security/api-tokens)
  - Tempo API token (from Tempo Settings → API Integration)

### Installation

1. Clone this repository:
```bash
git clone https://github.com/HumphreyCirium/ProductOwnerScripts.git
cd ProductOwnerScripts
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Configuration

You can configure the script using either a JSON configuration file or environment variables.

#### Option 1: Configuration File

1. Copy the example configuration:
```bash
cp config.example.json config.json
```

2. Edit `config.json` with your details:
```json
{
  "jira": {
    "url": "https://your-instance.atlassian.net",
    "email": "your-email@example.com",
    "api_token": "YOUR_JIRA_API_TOKEN"
  },
  "tempo": {
    "api_token": "YOUR_TEMPO_API_TOKEN"
  },
  "parameters": {
    "date_from": "2024-01-01",
    "date_to": "2024-01-31",
    "user_ids": [],
    "account_keys": [],
    "project_keys": []
  },
  "output": {
    "format": "excel",
    "directory": "output",
    "filename_prefix": "tempo_report"
  }
}
```

#### Option 2: Environment Variables

Create a `.env` file:
```bash
JIRA_URL=https://your-instance.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your_jira_token
TEMPO_API_TOKEN=your_tempo_token
DATE_FROM=2024-01-01
DATE_TO=2024-01-31
OUTPUT_FORMAT=excel
OUTPUT_DIR=output
OUTPUT_PREFIX=tempo_report
```

### Usage

#### Basic Usage

Run with configuration file:
```bash
python tempo_timesheet_analyzer.py -c config.json
```

Run with environment variables:
```bash
python tempo_timesheet_analyzer.py
```

#### Advanced Usage

Override date range:
```bash
python tempo_timesheet_analyzer.py -c config.json --date-from 2024-02-01 --date-to 2024-02-29
```

Specify output format:
```bash
python tempo_timesheet_analyzer.py -c config.json --format csv
```

Full example with all options:
```bash
python tempo_timesheet_analyzer.py \
  -c config.json \
  --date-from 2024-01-01 \
  --date-to 2024-01-31 \
  --format excel
```

### Output

The script generates reports in your specified output directory (default: `output/`):

#### Excel Output (Default)
A single Excel file with multiple sheets:
- **Summary**: Hours grouped by team member, account code, and ticket
- **Team Summary**: Total hours and worklog count per team member
- **Detailed Worklogs**: All individual worklog entries

#### CSV Output
Three separate CSV files:
- `tempo_report_summary_<timestamp>.csv`: Summary report
- `tempo_report_team_summary_<timestamp>.csv`: Team totals
- `tempo_report_detail_<timestamp>.csv`: Detailed worklogs

### Example Output

```
============================================================
Tempo Timesheet Analysis
============================================================

Fetching worklogs from 2024-01-01 to 2024-01-31...
  Fetched 150 worklogs so far...
✓ Total worklogs fetched: 150

Fetching account information...
✓ Fetched 12 accounts

Processing worklogs...
✓ Processed 150 worklog entries

Generating summary report...
✓ Generated summary with 45 rows

============================================================
Summary Statistics
============================================================
Total hours logged: 1200.50
Number of team members: 8
Number of unique issues: 35
Number of worklogs: 150

Top 5 Team Members by Hours:
    team_member  total_hours  worklog_count
    John Smith        180.25             25
    Jane Doe          165.50             22
    Bob Wilson        142.75             18
    Alice Brown       138.00             20
    Charlie Davis     125.25             15

✓ Exported to Excel: output/tempo_report_20240115_143022.xlsx

============================================================
✓ Analysis complete!
Report generated: output/tempo_report_20240115_143022.xlsx
============================================================
```

### Report Columns

#### Summary Report
- `team_member`: Name of the team member
- `account_code`: Tempo account code
- `account_name`: Tempo account name
- `issue_key`: Jira issue key (e.g., PROJ-123)
- `hours`: Total hours logged
- `description`: Sample work descriptions

#### Team Summary Report
- `team_member`: Name of the team member
- `total_hours`: Total hours logged by the team member
- `worklog_count`: Number of worklogs

#### Detailed Worklogs
- `date`: Date of the worklog
- `team_member`: Name of the team member
- `account_id`: Jira account ID
- `issue_key`: Jira issue key
- `issue_id`: Jira issue ID
- `account_code`: Tempo account code
- `account_name`: Tempo account name
- `hours`: Hours logged
- `description`: Work description
- `worklog_id`: Tempo worklog ID

### Filtering Data

To filter worklogs by specific users, add their account IDs to the configuration:

```json
{
  "parameters": {
    "user_ids": ["5d12345abcdef", "5d67890ghijkl"]
  }
}
```

To get user account IDs, you can use Jira's user search API or check the Tempo API responses.

### Troubleshooting

#### Authentication Issues
- Ensure your API tokens are valid and not expired
- Verify the Jira URL is correct (include https://)
- Check that your Jira email matches your account

#### No Data Returned
- Verify the date range has worklog entries
- Check that Tempo is properly configured in your Jira instance
- Ensure you have permission to view the worklogs

#### Import Errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Verify you're using Python 3.7 or higher: `python --version`

### API Rate Limits

The Tempo API has rate limits. If you encounter rate limiting:
- Reduce the date range
- Add delays between requests (the script handles pagination automatically)
- Contact Tempo support to check your API limits

### Security Best Practices

- ⚠️ **Never commit** `config.json` or `.env` files with real credentials
- Store API tokens securely
- Use environment variables for production deployments
- Regularly rotate API tokens
- Limit API token permissions to read-only access

### Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

### License

This project is provided as-is for use within your organization.

### Support

For issues or questions:
1. Check the Troubleshooting section
2. Review Tempo API documentation: https://apidocs.tempo.io/
3. Open an issue in this repository

### Changelog

#### Version 1.0.0
- Initial release
- Support for Tempo API v3
- Excel and CSV export options
- Configurable date ranges and filters
- Summary and detailed reports
