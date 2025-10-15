#!/usr/bin/env python3
"""
Sample test script for Tempo Timesheet Analyzer
This demonstrates the structure and usage without requiring real API access
"""

import json
import pandas as pd
from datetime import datetime
import os

# Sample worklog data structure (mimics Tempo API response)
SAMPLE_WORKLOGS = [
    {
        "tempoWorklogId": 1001,
        "issue": {"id": "10001", "key": "PROJ-123"},
        "timeSpentSeconds": 14400,  # 4 hours
        "startDate": "2024-01-15",
        "description": "Development work on feature",
        "author": {
            "accountId": "user1",
            "displayName": "John Smith"
        },
        "attributes": {
            "_account_": {"id": "acc1"}
        }
    },
    {
        "tempoWorklogId": 1002,
        "issue": {"id": "10002", "key": "PROJ-124"},
        "timeSpentSeconds": 10800,  # 3 hours
        "startDate": "2024-01-15",
        "description": "Code review",
        "author": {
            "accountId": "user2",
            "displayName": "Jane Doe"
        },
        "attributes": {
            "_account_": {"id": "acc1"}
        }
    },
    {
        "tempoWorklogId": 1003,
        "issue": {"id": "10001", "key": "PROJ-123"},
        "timeSpentSeconds": 7200,  # 2 hours
        "startDate": "2024-01-16",
        "description": "Testing and bug fixes",
        "author": {
            "accountId": "user1",
            "displayName": "John Smith"
        },
        "attributes": {
            "_account_": {"id": "acc2"}
        }
    }
]

# Sample account data (mimics Tempo API response)
SAMPLE_ACCOUNTS = {
    "acc1": {
        "id": "acc1",
        "key": "DEV-001",
        "name": "Development Account"
    },
    "acc2": {
        "id": "acc2",
        "key": "TEST-001",
        "name": "Testing Account"
    }
}


def process_sample_data():
    """Process sample data and generate reports."""
    print("=" * 60)
    print("Tempo Timesheet Analyzer - Sample Data Test")
    print("=" * 60)
    
    # Process worklogs
    processed_data = []
    for worklog in SAMPLE_WORKLOGS:
        author = worklog.get("author", {})
        issue = worklog.get("issue", {})
        account_id = worklog.get("attributes", {}).get("_account_", {}).get("id")
        
        account_info = SAMPLE_ACCOUNTS.get(account_id, {})
        account_key = account_info.get("key", account_id)
        account_name = account_info.get("name", "Unknown")
        
        time_spent_seconds = worklog.get("timeSpentSeconds", 0)
        hours = time_spent_seconds / 3600.0
        
        processed_data.append({
            "date": worklog.get("startDate"),
            "team_member": author.get("displayName", "Unknown"),
            "account_id": author.get("accountId"),
            "issue_key": issue.get("key", "No Issue"),
            "issue_id": issue.get("id"),
            "account_code": account_key,
            "account_name": account_name,
            "hours": hours,
            "description": worklog.get("description", ""),
            "worklog_id": worklog.get("tempoWorklogId")
        })
    
    df = pd.DataFrame(processed_data)
    print(f"\n✓ Processed {len(df)} sample worklog entries")
    
    # Generate summary
    summary = df.groupby(
        ["team_member", "account_code", "account_name", "issue_key"],
        dropna=False
    ).agg({
        "hours": "sum",
        "description": lambda x: " | ".join(x.dropna().unique()[:3])
    }).reset_index()
    
    summary = summary.sort_values(["team_member", "hours"], ascending=[True, False])
    summary["hours"] = summary["hours"].round(2)
    
    # Team summary
    team_summary = df.groupby("team_member").agg({
        "hours": "sum",
        "issue_key": "count"
    }).reset_index()
    team_summary.columns = ["team_member", "total_hours", "worklog_count"]
    team_summary["total_hours"] = team_summary["total_hours"].round(2)
    
    # Print results
    print("\n" + "=" * 60)
    print("Summary by Team Member, Account, and Issue")
    print("=" * 60)
    print(summary.to_string(index=False))
    
    print("\n" + "=" * 60)
    print("Team Summary")
    print("=" * 60)
    print(team_summary.to_string(index=False))
    
    print("\n" + "=" * 60)
    print("Detailed Worklogs")
    print("=" * 60)
    print(df.to_string(index=False))
    
    # Save sample output
    os.makedirs("output", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    with pd.ExcelWriter(f"output/sample_report_{timestamp}.xlsx", engine='openpyxl') as writer:
        summary.to_excel(writer, sheet_name="Summary", index=False)
        team_summary.to_excel(writer, sheet_name="Team Summary", index=False)
        df.to_excel(writer, sheet_name="Detailed Worklogs", index=False)
    
    print(f"\n✓ Sample report saved to: output/sample_report_{timestamp}.xlsx")
    
    print("\n" + "=" * 60)
    print("✓ Sample test complete!")
    print("=" * 60)


if __name__ == "__main__":
    process_sample_data()
