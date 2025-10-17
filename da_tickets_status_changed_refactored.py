#!/usr/bin/env python3
"""
DA Tickets Status Changed in Sprint Report
Refactored version using JiraReportBase.
"""

from jira_report_base import JiraReportBase, JiraUtilities, ReportConfig


class DATicketsStatusChangedReport(JiraReportBase):
    """Report for DA tickets with status changes in the last sprint."""
    
    def __init__(self, config_file: str = 'config.ini'):
        """Initialize the DA status change report."""
        super().__init__(config_file)
        self.board_name = self.config.get('board_name', 'DA')
        self.sprint_days = ReportConfig.ONE_SPRINT_DAYS
    
    def build_jql_query(self) -> str:
        """Build JQL query for tickets with status changes in the last sprint."""
        cutoff_date = self.get_date_days_ago(self.sprint_days)
        cutoff_date_str = self.format_date_for_jql(cutoff_date)
        
        return f'project = "{self.board_name}" AND (status changed AFTER "{cutoff_date_str}")'
    
    def get_required_fields(self) -> list:
        """Get required fields for this report."""
        return ["summary", "status", "updated"]
    
    def process_issues(self, issues: list) -> list:
        """Process raw issues into DA report format."""
        processed_data = []
        
        for issue in issues:
            updated_raw = JiraUtilities.extract_field_value(issue, 'fields.updated')
            processed_item = {
                'ID': issue.get('key', 'N/A'),
                'Summary': JiraUtilities.extract_field_value(issue, 'fields.summary'),
                'Status': JiraUtilities.safe_get_status(issue),
                'Last Updated': JiraUtilities.format_jira_date(updated_raw),
            }
            processed_data.append(processed_item)
        
        return processed_data
    
    def get_csv_headers(self) -> list:
        """Get CSV headers for DA report."""
        return ['ID', 'Summary', 'Status', 'Last Updated']
    
    def get_output_filename(self) -> str:
        """Get output filename for DA report."""
        return str(ReportConfig.OUTPUT_DIR / "da status change.csv")
    
    def display_results(self, processed_data: list) -> None:
        """Display results in DA report format."""
        print(f"\n📋 DA Tickets with Status Changes (Last {self.sprint_days} days):")
        print("-" * 80)
        
        if not processed_data:
            print("No tickets found with status changes in the specified period.")
            return
        
        for item in processed_data:
            print(f"ID: {item['ID']}, Summary: {item['Summary']}, Status: {item['Status']}")


def main():
    """Main function to run the DA tickets status change report."""
    report = DATicketsStatusChangedReport()
    report.run_report()


if __name__ == "__main__":
    main()