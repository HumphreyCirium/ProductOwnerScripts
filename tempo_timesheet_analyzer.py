#!/usr/bin/env python3
"""
Tempo Timesheet Analysis Script
Analyzes Tempo timesheet data and generates reports summarized by account code,
ticket, and team member.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
import argparse

import pandas as pd
import requests
from jira import JIRA
from dotenv import load_dotenv


class TempoTimesheetAnalyzer:
    """Analyzes Tempo timesheet data and generates reports."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize the Tempo Timesheet Analyzer.
        
        Args:
            config_path: Path to configuration file (JSON format)
        """
        load_dotenv()
        self.config = self._load_config(config_path)
        self.jira_client = None
        self.tempo_api_url = "https://api.tempo.io/core/3"
        self._authenticate()
        
    def _load_config(self, config_path: str = None) -> Dict:
        """Load configuration from file or environment variables."""
        config = {}
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            # Load from environment variables as fallback
            config = {
                "jira": {
                    "url": os.getenv("JIRA_URL", ""),
                    "email": os.getenv("JIRA_EMAIL", ""),
                    "api_token": os.getenv("JIRA_API_TOKEN", "")
                },
                "tempo": {
                    "api_token": os.getenv("TEMPO_API_TOKEN", "")
                },
                "parameters": {
                    "date_from": os.getenv("DATE_FROM", "2024-01-01"),
                    "date_to": os.getenv("DATE_TO", "2024-01-31"),
                    "user_ids": [],
                    "account_keys": [],
                    "project_keys": []
                },
                "output": {
                    "format": os.getenv("OUTPUT_FORMAT", "excel"),
                    "directory": os.getenv("OUTPUT_DIR", "output"),
                    "filename_prefix": os.getenv("OUTPUT_PREFIX", "tempo_report")
                }
            }
        
        return config
    
    def _authenticate(self):
        """Authenticate with Jira and Tempo APIs."""
        jira_config = self.config.get("jira", {})
        
        if jira_config.get("url") and jira_config.get("email") and jira_config.get("api_token"):
            try:
                self.jira_client = JIRA(
                    server=jira_config["url"],
                    basic_auth=(jira_config["email"], jira_config["api_token"])
                )
                print("✓ Successfully authenticated with Jira")
            except Exception as e:
                print(f"⚠ Warning: Could not authenticate with Jira: {e}")
                self.jira_client = None
        
        tempo_token = self.config.get("tempo", {}).get("api_token")
        if not tempo_token:
            raise ValueError("Tempo API token is required. Set it in config or TEMPO_API_TOKEN environment variable.")
        
        self.tempo_headers = {
            "Authorization": f"Bearer {tempo_token}",
            "Content-Type": "application/json"
        }
        print("✓ Tempo API token configured")
    
    def fetch_worklogs(self, date_from: str, date_to: str, 
                       user_ids: List[str] = None) -> List[Dict]:
        """
        Fetch worklogs from Tempo API.
        
        Args:
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            user_ids: Optional list of user IDs to filter by
            
        Returns:
            List of worklog dictionaries
        """
        print(f"\nFetching worklogs from {date_from} to {date_to}...")
        
        all_worklogs = []
        offset = 0
        limit = 1000
        
        while True:
            params = {
                "from": date_from,
                "to": date_to,
                "offset": offset,
                "limit": limit
            }
            
            try:
                response = requests.get(
                    f"{self.tempo_api_url}/worklogs",
                    headers=self.tempo_headers,
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                results = data.get("results", [])
                if not results:
                    break
                
                all_worklogs.extend(results)
                offset += limit
                
                print(f"  Fetched {len(all_worklogs)} worklogs so far...")
                
                # Check if we have all results
                if len(results) < limit:
                    break
                    
            except requests.exceptions.RequestException as e:
                print(f"✗ Error fetching worklogs: {e}")
                break
        
        # Filter by user IDs if specified
        if user_ids:
            all_worklogs = [
                wl for wl in all_worklogs 
                if wl.get("author", {}).get("accountId") in user_ids
            ]
        
        print(f"✓ Total worklogs fetched: {len(all_worklogs)}")
        return all_worklogs
    
    def fetch_accounts(self) -> Dict[str, Dict]:
        """
        Fetch account information from Tempo API.
        
        Returns:
            Dictionary mapping account IDs to account details
        """
        print("\nFetching account information...")
        
        try:
            response = requests.get(
                f"{self.tempo_api_url}/accounts",
                headers=self.tempo_headers
            )
            response.raise_for_status()
            data = response.json()
            
            accounts = {
                account["id"]: account 
                for account in data.get("results", [])
            }
            
            print(f"✓ Fetched {len(accounts)} accounts")
            return accounts
            
        except requests.exceptions.RequestException as e:
            print(f"⚠ Warning: Could not fetch accounts: {e}")
            return {}
    
    def process_worklogs(self, worklogs: List[Dict], 
                        accounts: Dict[str, Dict] = None) -> pd.DataFrame:
        """
        Process worklogs into a structured DataFrame.
        
        Args:
            worklogs: List of worklog dictionaries
            accounts: Dictionary of account information
            
        Returns:
            Pandas DataFrame with processed worklog data
        """
        print("\nProcessing worklogs...")
        
        if not worklogs:
            print("⚠ No worklogs to process")
            return pd.DataFrame()
        
        processed_data = []
        
        for worklog in worklogs:
            # Extract basic information
            author = worklog.get("author", {})
            issue = worklog.get("issue", {})
            
            # Get account information
            account_id = worklog.get("attributes", {}).get("_account_", {}).get("id")
            account_key = None
            account_name = None
            
            if account_id and accounts and account_id in accounts:
                account_info = accounts[account_id]
                account_key = account_info.get("key", account_id)
                account_name = account_info.get("name", "Unknown")
            elif account_id:
                account_key = account_id
                account_name = "Unknown"
            
            # Calculate hours
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
        print(f"✓ Processed {len(df)} worklog entries")
        return df
    
    def generate_summary_report(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate summary report grouped by team member, account code, and ticket.
        
        Args:
            df: DataFrame with processed worklog data
            
        Returns:
            Summary DataFrame
        """
        print("\nGenerating summary report...")
        
        if df.empty:
            print("⚠ No data to summarize")
            return pd.DataFrame()
        
        # Group by team member, account code, and issue
        summary = df.groupby(
            ["team_member", "account_code", "account_name", "issue_key"],
            dropna=False
        ).agg({
            "hours": "sum",
            "description": lambda x: " | ".join(x.dropna().unique()[:3])  # First 3 unique descriptions
        }).reset_index()
        
        # Sort by team member and hours (descending)
        summary = summary.sort_values(
            ["team_member", "hours"], 
            ascending=[True, False]
        )
        
        # Round hours to 2 decimal places
        summary["hours"] = summary["hours"].round(2)
        
        print(f"✓ Generated summary with {len(summary)} rows")
        return summary
    
    def generate_team_member_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate summary report by team member only.
        
        Args:
            df: DataFrame with processed worklog data
            
        Returns:
            Summary DataFrame by team member
        """
        if df.empty:
            return pd.DataFrame()
        
        summary = df.groupby("team_member").agg({
            "hours": "sum",
            "issue_key": "count"
        }).reset_index()
        
        summary.columns = ["team_member", "total_hours", "worklog_count"]
        summary["total_hours"] = summary["total_hours"].round(2)
        summary = summary.sort_values("total_hours", ascending=False)
        
        return summary
    
    def export_to_csv(self, df: pd.DataFrame, filename: str):
        """Export DataFrame to CSV file."""
        output_dir = self.config.get("output", {}).get("directory", "output")
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, filename)
        df.to_csv(filepath, index=False)
        print(f"✓ Exported to CSV: {filepath}")
        return filepath
    
    def export_to_excel(self, dataframes: Dict[str, pd.DataFrame], filename: str):
        """
        Export multiple DataFrames to Excel file with separate sheets.
        
        Args:
            dataframes: Dictionary mapping sheet names to DataFrames
            filename: Output filename
        """
        output_dir = self.config.get("output", {}).get("directory", "output")
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            for sheet_name, df in dataframes.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        print(f"✓ Exported to Excel: {filepath}")
        return filepath
    
    def run(self, date_from: str = None, date_to: str = None, 
            output_format: str = None) -> str:
        """
        Run the complete timesheet analysis workflow.
        
        Args:
            date_from: Start date (YYYY-MM-DD), overrides config
            date_to: End date (YYYY-MM-DD), overrides config
            output_format: Output format ('csv' or 'excel'), overrides config
            
        Returns:
            Path to generated report file
        """
        params = self.config.get("parameters", {})
        
        # Use provided dates or fall back to config
        date_from = date_from or params.get("date_from")
        date_to = date_to or params.get("date_to")
        user_ids = params.get("user_ids", [])
        
        # Use provided format or fall back to config
        output_config = self.config.get("output", {})
        output_format = output_format or output_config.get("format", "excel")
        
        print("=" * 60)
        print("Tempo Timesheet Analysis")
        print("=" * 60)
        
        # Fetch data
        worklogs = self.fetch_worklogs(date_from, date_to, user_ids)
        accounts = self.fetch_accounts()
        
        # Process data
        df = self.process_worklogs(worklogs, accounts)
        
        if df.empty:
            print("\n✗ No data to process. Please check your date range and filters.")
            return None
        
        # Generate summaries
        summary_df = self.generate_summary_report(df)
        team_summary_df = self.generate_team_member_summary(df)
        
        # Print quick stats
        print("\n" + "=" * 60)
        print("Summary Statistics")
        print("=" * 60)
        print(f"Total hours logged: {df['hours'].sum():.2f}")
        print(f"Number of team members: {df['team_member'].nunique()}")
        print(f"Number of unique issues: {df['issue_key'].nunique()}")
        print(f"Number of worklogs: {len(df)}")
        
        print("\nTop 5 Team Members by Hours:")
        print(team_summary_df.head().to_string(index=False))
        
        # Export results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = output_config.get("filename_prefix", "tempo_report")
        
        if output_format.lower() == "csv":
            # Export to separate CSV files
            summary_file = f"{prefix}_summary_{timestamp}.csv"
            detail_file = f"{prefix}_detail_{timestamp}.csv"
            team_file = f"{prefix}_team_summary_{timestamp}.csv"
            
            self.export_to_csv(summary_df, summary_file)
            self.export_to_csv(df, detail_file)
            self.export_to_csv(team_summary_df, team_file)
            
            return os.path.join(output_config.get("directory", "output"), summary_file)
        else:
            # Export to Excel with multiple sheets
            excel_file = f"{prefix}_{timestamp}.xlsx"
            
            dataframes = {
                "Summary": summary_df,
                "Team Summary": team_summary_df,
                "Detailed Worklogs": df
            }
            
            return self.export_to_excel(dataframes, excel_file)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Analyze Tempo timesheet data and generate reports"
    )
    parser.add_argument(
        "-c", "--config",
        help="Path to configuration file (JSON format)",
        default=None
    )
    parser.add_argument(
        "--date-from",
        help="Start date (YYYY-MM-DD)",
        default=None
    )
    parser.add_argument(
        "--date-to",
        help="End date (YYYY-MM-DD)",
        default=None
    )
    parser.add_argument(
        "--format",
        help="Output format (csv or excel)",
        choices=["csv", "excel"],
        default=None
    )
    
    args = parser.parse_args()
    
    try:
        analyzer = TempoTimesheetAnalyzer(config_path=args.config)
        output_file = analyzer.run(
            date_from=args.date_from,
            date_to=args.date_to,
            output_format=args.format
        )
        
        if output_file:
            print("\n" + "=" * 60)
            print("✓ Analysis complete!")
            print(f"Report generated: {output_file}")
            print("=" * 60)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
