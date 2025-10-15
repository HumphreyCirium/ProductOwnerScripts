# Quick Start Guide - Tempo Timesheet Analyzer

This guide will help you quickly get started with the Tempo Timesheet Analyzer.

## Prerequisites

1. Python 3.7+ installed
2. Tempo API token (get from Tempo Settings → API Integration)
3. Jira API token (get from https://id.atlassian.com/manage-profile/security/api-tokens)

## Quick Setup (5 minutes)

### Step 1: Install Dependencies

```bash
# Clone the repository (if not already done)
git clone https://github.com/HumphreyCirium/ProductOwnerScripts.git
cd ProductOwnerScripts

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### Step 2: Configure API Access

**Option A: Using Configuration File (Recommended)**

```bash
# Copy the example config
cp config.example.json config.json

# Edit config.json with your actual values:
# - Replace JIRA_URL with your instance (e.g., https://company.atlassian.net)
# - Replace your-email@example.com with your Jira email
# - Replace YOUR_JIRA_API_TOKEN with your actual Jira API token
# - Replace YOUR_TEMPO_API_TOKEN with your actual Tempo API token
# - Adjust date_from and date_to for your desired date range
```

**Option B: Using Environment Variables**

```bash
# Copy the example .env
cp .env.example .env

# Edit .env with your actual values
```

### Step 3: Run the Analyzer

```bash
# Basic run with config file
python tempo_timesheet_analyzer.py -c config.json

# Or with environment variables
python tempo_timesheet_analyzer.py

# Override date range
python tempo_timesheet_analyzer.py -c config.json --date-from 2024-01-01 --date-to 2024-01-31
```

### Step 4: View Results

Reports are saved in the `output/` directory:
- **Excel format** (default): Single file with 3 sheets (Summary, Team Summary, Detailed Worklogs)
- **CSV format**: 3 separate CSV files

## Common Use Cases

### Analyze Last Month's Timesheets

```bash
python tempo_timesheet_analyzer.py -c config.json --date-from 2024-01-01 --date-to 2024-01-31
```

### Generate CSV Reports Instead of Excel

```bash
python tempo_timesheet_analyzer.py -c config.json --format csv
```

### Analyze Specific Date Range

```bash
python tempo_timesheet_analyzer.py \
  -c config.json \
  --date-from 2024-02-01 \
  --date-to 2024-02-15
```

## Testing Without API Access

Run the sample data test to see how the tool works:

```bash
python test_sample_data.py
```

This will generate a sample report in `output/` using mock data.

## Output Interpretation

### Summary Report
Shows total hours grouped by:
- Team Member
- Account Code (Tempo billing account)
- Issue Key (Jira ticket)

### Team Summary Report
Shows:
- Total hours per team member
- Number of worklogs per team member

### Detailed Worklogs
Shows all individual time entries with:
- Date, team member, issue, account
- Hours logged and descriptions

## Troubleshooting

### "Tempo API token is required" Error
- Make sure your Tempo API token is set in config.json or .env
- Verify the token is valid (not expired)

### "Could not authenticate with Jira" Warning
- This is optional - the tool will still fetch Tempo data
- Check your Jira URL, email, and API token

### No Data Returned
- Check your date range has actual worklogs
- Verify you have access to view the worklogs
- Try a broader date range

## Next Steps

- Review the full [README.md](README.md) for detailed documentation
- Explore filtering options (user IDs, account keys)
- Customize output directory and filename prefix
- Set up automated reporting with cron jobs or scheduled tasks

## Support

If you encounter issues:
1. Check [README.md](README.md) troubleshooting section
2. Verify API tokens are correct and have proper permissions
3. Review Tempo API documentation: https://apidocs.tempo.io/
4. Open an issue in the repository

## Security Reminder

⚠️ **Never commit config.json or .env files with real credentials!**

These files are already in .gitignore, but be careful when sharing or committing code.
