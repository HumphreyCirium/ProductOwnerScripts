#!/usr/bin/env python3
"""
Example: Custom Jira Report using JiraReportBase
This demonstrates how easy it is to create new reports with the refactored base class.
"""

from jira_report_base import JiraReportBase, JiraUtilities, ReportConfig


class RecentlyCreatedTicketsReport(JiraReportBase):
    """Example report: Tickets created in the last week."""
    
    def __init__(self, config_file: str = 'config.ini', days: int = 7):
        """Initialize the recently created tickets report."""
        super().__init__(config_file)
        self.days = days
        self.board_name = self.config.get('board_name', 'DA')
    
    def build_jql_query(self) -> str:
        """Build JQL query for recently created tickets."""
        cutoff_date = self.get_date_days_ago(self.days)
        cutoff_date_str = self.format_date_for_jql(cutoff_date)
        
        return f'project = "{self.board_name}" AND created >= "{cutoff_date_str}"'
    
    def get_required_fields(self) -> list:
        """Get required fields for this report."""
        return ["summary", "status", "assignee", "created", "reporter"]
    
    def process_issues(self, issues: list) -> list:
        """Process raw issues into report format."""
        processed_data = []
        
        for issue in issues:
            reporter = JiraUtilities.extract_field_value(issue, 'fields.reporter')
            reporter_name = reporter.get('displayName', 'Unknown') if isinstance(reporter, dict) else 'Unknown'
            
            processed_item = {
                'ID': issue.get('key', 'N/A'),
                'Summary': JiraUtilities.extract_field_value(issue, 'fields.summary'),
                'Status': JiraUtilities.safe_get_status(issue),
                'Assignee': JiraUtilities.safe_get_assignee(issue),
                'Reporter': reporter_name,
                'Created': JiraUtilities.extract_field_value(issue, 'fields.created'),
                'URL': self.get_issue_url(issue.get('key', ''))
            }
            processed_data.append(processed_item)
        
        return processed_data
    
    def get_csv_headers(self) -> list:
        """Get CSV headers for this report."""
        return ['ID', 'Summary', 'Status', 'Assignee', 'Reporter', 'Created', 'URL']
    
    def get_output_filename(self) -> str:
        """Get output filename for this report."""
        return str(ReportConfig.OUTPUT_DIR / f"recently_created_tickets_{self.days}days.csv")
    
    def display_results(self, processed_data: list) -> None:
        """Display results with custom formatting."""
        print(f"\n🆕 Recently Created Tickets (Last {self.days} days):")
        print("-" * 80)
        
        if not processed_data:
            print(f"No tickets created in the last {self.days} days.")
            return
        
        for item in processed_data:
            print(f"🎫 {item['ID']}: {item['Summary']}")
            print(f"   Status: {item['Status']} | Assignee: {item['Assignee']}")
            print(f"   Reporter: {item['Reporter']} | Created: {item['Created']}")
            print()


def main():
    """Main function to run the recently created tickets report."""
    # You can customize the number of days
    report = RecentlyCreatedTicketsReport(days=7)  # Last 7 days
    report.run_report()


if __name__ == "__main__":
    main()