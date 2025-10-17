#!/usr/bin/env python3
"""
Stale Tickets Report
Refactored version using JiraReportBase - reports tickets with no status change in the last 3 months.
"""

from jira_report_base import JiraReportBase, JiraUtilities, ReportConfig
from datetime import datetime


class StaleTicketsReport(JiraReportBase):
    """Report for tickets with no status change in the last 3 months."""
    
    def __init__(self, config_file: str = 'config.ini', months: int = 3):
        """Initialize the stale tickets report."""
        super().__init__(config_file)
        self.months = months
        self.stale_days = months * 30
        self.projects = ReportConfig.FDA_FDP_PROJECTS
        self.boards_info = [
            {'project': 'FDA', 'board_id': 740, 'name': 'FDA Board'},
            {'project': 'FDP', 'board_id': 728, 'name': 'FDP Board'}
        ]
    
    def build_jql_query(self) -> str:
        """Build JQL query for stale tickets across multiple projects."""
        cutoff_date = self.get_date_days_ago(self.stale_days)
        cutoff_date_str = self.format_date_for_jql(cutoff_date)
        
        # Build query for all projects
        project_clause = " OR ".join([f"project = {project}" for project in self.projects])
        
        return (f'({project_clause}) AND '
                f'status changed BEFORE "{cutoff_date_str}" AND '
                f'(updated >= "{cutoff_date_str}" OR created >= "{cutoff_date_str}")')
    
    def get_required_fields(self) -> list:
        """Get required fields for stale tickets report."""
        return ["summary", "status", "assignee", "created", "updated", "statuscategorychangedate"]
    
    def process_issues(self, issues: list) -> list:
        """Process raw issues into stale tickets report format."""
        processed_data = []
        
        for issue in issues:
            created_raw = JiraUtilities.extract_field_value(issue, 'fields.created')
            updated_raw = JiraUtilities.extract_field_value(issue, 'fields.updated')
            status_changed_raw = JiraUtilities.extract_field_value(issue, 'fields.statuscategorychangedate')
            
            processed_item = {
                'ID': issue.get('key', 'N/A'),
                'Summary': JiraUtilities.extract_field_value(issue, 'fields.summary'),
                'Status': JiraUtilities.safe_get_status(issue),
                'Assignee': JiraUtilities.safe_get_assignee(issue),
                'Created': JiraUtilities.format_jira_date(created_raw),
                'Last Updated': JiraUtilities.format_jira_date(updated_raw),
                'Status Changed': JiraUtilities.format_jira_date(status_changed_raw),
                'URL': self.get_issue_url(issue.get('key', ''))
            }
            processed_data.append(processed_item)
        
        return processed_data
    
    def get_csv_headers(self) -> list:
        """Get CSV headers for stale tickets report."""
        return ['ID', 'Summary', 'Status', 'Assignee', 'Created', 'Last Updated', 'Status Changed', 'URL']
    
    def get_output_filename(self) -> str:
        """Get output filename for stale tickets report."""
        return str(ReportConfig.OUTPUT_DIR / "Stale Tickets Report.csv")
    
    def display_results(self, processed_data: list) -> None:
        """Display results with detailed formatting by board."""
        print(f"\n📋 Stale Tickets Report (No Status Change in Last {self.months} months):")
        print("=" * 80)
        
        if not processed_data:
            print("🎉 No stale tickets found across all boards!")
            return
        
        # Group by project for display
        project_groups = {}
        for item in processed_data:
            project = item['ID'].split('-')[0]  # Extract project from ticket key
            if project not in project_groups:
                project_groups[project] = []
            project_groups[project].append(item)
        
        total_stale = 0
        
        for board_info in self.boards_info:
            project = board_info['project']
            board_name = board_info['name']
            
            project_tickets = project_groups.get(project, [])
            
            print(f"\n🔍 {board_name} (Project: {project})")
            print("-" * 60)
            
            if project_tickets:
                print(f"Found {len(project_tickets)} stale ticket(s):")
                
                for item in project_tickets:
                    print(f"\n  📋 {item['ID']}: {item['Summary']}")
                    print(f"     Status: {item['Status']}")
                    print(f"     Assignee: {item['Assignee']}")
                    print(f"     Last Updated: {item['Last Updated']}")
                    print(f"     Status Changed: {item['Status Changed']}")
                    print(f"     URL: {item['URL']}")
                
                total_stale += len(project_tickets)
            else:
                print("✅ No stale tickets found.")
        
        print("\n" + "=" * 80)
        print(f"📊 Total stale tickets across all boards: {total_stale}")
        print("=" * 80)
    
    def run_report_by_project(self) -> None:
        """Run report with per-project breakdown (alternative method)."""
        print("=" * 80)
        print(f"🔍 Stale Tickets Report - Individual Project Analysis")
        print("=" * 80)
        
        all_processed_data = []
        
        for board_info in self.boards_info:
            project = board_info['project']
            board_name = board_info['name']
            
            print(f"\n🔍 Analyzing {board_name} (Project: {project})")
            print("-" * 60)
            
            # Build project-specific query
            cutoff_date = self.get_date_days_ago(self.stale_days)
            cutoff_date_str = self.format_date_for_jql(cutoff_date)
            
            project_jql = (f'project = {project} AND '
                          f'status changed BEFORE "{cutoff_date_str}" AND '
                          f'(updated >= "{cutoff_date_str}" OR created >= "{cutoff_date_str}")')
            
            # Get issues for this project
            raw_issues = self.search_issues(project_jql, self.get_required_fields())
            processed_issues = self.process_issues(raw_issues)
            
            if processed_issues:
                print(f"Found {len(processed_issues)} stale ticket(s)")
                all_processed_data.extend(processed_issues)
            else:
                print("✅ No stale tickets found")
        
        # Write combined CSV
        if all_processed_data:
            self.write_csv(
                self.get_output_filename(),
                all_processed_data,
                self.get_csv_headers()
            )
        
        print(f"\n📊 Total stale tickets: {len(all_processed_data)}")


def main():
    """Main function to run the stale tickets report."""
    # You can choose between two approaches:
    
    # Approach 1: Single query across all projects
    report = StaleTicketsReport()
    report.run_report()
    
    # Approach 2: Individual project queries (uncomment to use)
    # report = StaleTicketsReport()
    # report.run_report_by_project()


if __name__ == "__main__":
    main()