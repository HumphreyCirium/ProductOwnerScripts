#!/usr/bin/env python3
"""
Shared Jira Report Library
Base class and utilities for Jira reporting scripts.
"""

import configparser
import sys
import csv
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod


class JiraReportBase(ABC):
    """Base class for Jira reporting scripts."""
    
    def __init__(self, config_file: str = 'config.ini'):
        """Initialize the Jira report with configuration."""
        self.config = self._load_config(config_file)
        self.server = self.config.get('server')
        self.email = self.config.get('email')
        self.api_token = self.config.get('api_token')
        self.base_url = f"{self.server}/rest/api/3/search/jql"
    
    def _load_config(self, config_file: str) -> Dict[str, str]:
        """Load Jira configuration from config.ini file."""
        config = configparser.ConfigParser()
        config.read(config_file)
        
        if 'jira' not in config:
            print("Error: config.ini file not found or missing [jira] section.")
            print("Please create config.ini based on config.ini.example")
            sys.exit(1)
        
        return config['jira']
    
    def search_issues(self, jql_query: str, fields: List[str] = None, max_results: int = 1000) -> List[Dict]:
        """
        Execute a JQL query and return matching issues.
        
        Args:
            jql_query: JQL query string
            fields: List of fields to retrieve (default: summary, status)
            max_results: Maximum number of results to return
            
        Returns:
            List of issue dictionaries
        """
        if fields is None:
            fields = ["summary", "status"]
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        params = {
            "jql": jql_query,
            "fields": ",".join(fields),
            "maxResults": max_results
        }
        
        try:
            print(f"Executing JQL: {jql_query}")
            print(f"Requesting fields: {', '.join(fields)}")
            response = requests.get(
                self.base_url,
                headers=headers,
                params=params,
                auth=HTTPBasicAuth(self.email, self.api_token)
            )
            
            if response.status_code == 200:
                data = response.json()
                issues = data.get('issues', [])
                print(f"Found {len(issues)} issue(s)")
                return issues
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"Error executing search: {e}")
            return []
    
    def write_csv(self, filename: str, data: List[Dict[str, Any]], headers: List[str]) -> None:
        """
        Write data to CSV file.
        
        Args:
            filename: Output CSV filename
            data: List of dictionaries containing the data
            headers: List of column headers
        """
        try:
            # Create output directory if it doesn't exist
            output_path = Path(filename)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                writer.writeheader()
                writer.writerows(data)
            
            print(f"✅ Data exported to {filename}")
            
        except Exception as e:
            print(f"❌ Error writing CSV: {e}")
    
    def format_date_for_jql(self, date_obj: datetime) -> str:
        """Format datetime object for JQL queries."""
        return date_obj.strftime('%Y-%m-%d')
    
    def get_date_days_ago(self, days: int) -> datetime:
        """Get a date N days ago from today."""
        return datetime.today() - timedelta(days=days)
    
    def get_issue_url(self, issue_key: str) -> str:
        """Generate URL for a Jira issue."""
        return f"{self.server}/browse/{issue_key}"
    
    @abstractmethod
    def build_jql_query(self) -> str:
        """Build the JQL query for this specific report. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def process_issues(self, issues: List[Dict]) -> List[Dict[str, Any]]:
        """Process raw issues into the desired output format. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def get_output_filename(self) -> str:
        """Get the output filename for this report. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def get_csv_headers(self) -> List[str]:
        """Get the CSV headers for this report. Must be implemented by subclasses."""
        pass
    
    def run_report(self) -> None:
        """Main method to run the report."""
        print("=" * 80)
        print(f"🔍 {self.__class__.__name__}")
        print("=" * 80)
        
        # Build and execute query
        jql_query = self.build_jql_query()
        required_fields = self.get_required_fields()
        print(f"📋 Required fields: {', '.join(required_fields)}")
        raw_issues = self.search_issues(jql_query, required_fields)
        
        if not raw_issues:
            print("📋 No issues found matching the criteria.")
            return
        
        # Process issues
        processed_data = self.process_issues(raw_issues)
        
        # Display results
        self.display_results(processed_data)
        
        # Write to CSV
        if processed_data:
            self.write_csv(
                self.get_output_filename(),
                processed_data,
                self.get_csv_headers()
            )
    
    def get_required_fields(self) -> List[str]:
        """Get list of Jira fields required for this report. Override if needed."""
        return ["summary", "status", "created", "updated"]
    
    def display_results(self, processed_data: List[Dict[str, Any]]) -> None:
        """Display results to console. Override for custom formatting."""
        print(f"\n📊 Results Summary:")
        print("-" * 40)
        
        for item in processed_data:
            for key, value in item.items():
                print(f"  {key}: {value}")
            print()


class JiraUtilities:
    """Utility functions for Jira operations."""
    
    @staticmethod
    def extract_field_value(issue: Dict, field_path: str, default: str = "N/A") -> str:
        """
        Extract a field value from an issue using dot notation.
        
        Args:
            issue: Issue dictionary
            field_path: Path to field (e.g., 'fields.status.name')
            default: Default value if field not found
            
        Returns:
            Field value or default
        """
        try:
            keys = field_path.split('.')
            value = issue
            for key in keys:
                value = value[key]
            return value if value is not None else default
        except (KeyError, TypeError):
            return default
    
    @staticmethod
    def safe_get_assignee(issue: Dict) -> str:
        """Safely extract assignee name from issue."""
        assignee = JiraUtilities.extract_field_value(issue, 'fields.assignee')
        if assignee == "N/A" or assignee is None:
            return "Unassigned"
        return assignee.get('displayName', 'Unassigned') if isinstance(assignee, dict) else str(assignee)
    
    @staticmethod
    def safe_get_status(issue: Dict) -> str:
        """Safely extract status name from issue."""
        status = JiraUtilities.extract_field_value(issue, 'fields.status')
        if status == "N/A" or status is None:
            return "Unknown"
        return status.get('name', 'Unknown') if isinstance(status, dict) else str(status)
    
    @staticmethod
    def format_jira_date(date_string: str, format_str: str = "%Y-%m-%d %H:%M") -> str:
        """
        Format a Jira date string into a more readable format, converted to UTC.
        
        Args:
            date_string: ISO 8601 date string from Jira (e.g., '2024-10-17T14:30:45.123+0000' or '2024-10-17T14:30:45.123-0700')
            format_str: Desired output format (default: 'YYYY-MM-DD HH:MM')
            
        Returns:
            Formatted date string in UTC or original if parsing fails
        """
        if not date_string or date_string == "N/A":
            return "N/A"
        
        try:
            from datetime import timezone
            
            # Parse ISO 8601 format with timezone offset
            # Examples: 
            #   2024-10-17T14:30:45.123+0000
            #   2024-10-17T14:30:45.123-0700
            #   2024-10-17T14:30:45+0000
            
            # Remove timezone for parsing, we'll handle it separately
            if '+' in date_string or date_string.count('-') > 2:
                # Find the timezone offset
                # Split on + or the last - (for negative offsets)
                if '+' in date_string:
                    time_part, tz_part = date_string.rsplit('+', 1)
                    tz_sign = 1
                else:
                    # Handle negative timezone like -0700
                    parts = date_string.rsplit('-', 1)
                    if len(parts) == 2 and len(parts[1]) == 4 and parts[1].isdigit():
                        time_part, tz_part = parts
                        tz_sign = -1
                    else:
                        # No timezone, treat as UTC
                        time_part = date_string
                        tz_part = "0000"
                        tz_sign = 1
                
                # Parse the time part
                if '.' in time_part:
                    # Has milliseconds
                    dt_naive = datetime.strptime(time_part, "%Y-%m-%dT%H:%M:%S.%f")
                else:
                    # No milliseconds
                    dt_naive = datetime.strptime(time_part, "%Y-%m-%dT%H:%M:%S")
                
                # Parse timezone offset (e.g., "0000" or "0700")
                tz_hours = int(tz_part[:2]) * tz_sign
                tz_minutes = int(tz_part[2:4]) * tz_sign
                tz_offset = timedelta(hours=tz_hours, minutes=tz_minutes)
                
                # Convert to UTC by subtracting the offset
                dt_utc = dt_naive - tz_offset
                
            else:
                # No timezone info, assume UTC
                if '.' in date_string:
                    dt_utc = datetime.strptime(date_string[:23], "%Y-%m-%dT%H:%M:%S.%f")
                else:
                    dt_utc = datetime.strptime(date_string[:19], "%Y-%m-%dT%H:%M:%S")
            
            return dt_utc.strftime(format_str)
        except (ValueError, AttributeError, IndexError) as e:
            # If parsing fails, return original
            return date_string


# Example configurations for common report patterns
class ReportConfig:
    """Common report configurations."""
    
    # Common output directory
    OUTPUT_DIR = Path("C:/Users/pasleyh/OneDrive - Reed Elsevier Group ICO Reed Elsevier Inc/Documents/Scripts")
    
    # Common boards/projects
    DA_PROJECTS = ["DA"]  # Adjust based on your actual project keys
    FDA_FDP_PROJECTS = ["FDA", "FDP"]
    
    # Common time periods
    ONE_SPRINT_DAYS = 27
    THREE_MONTHS_DAYS = 90