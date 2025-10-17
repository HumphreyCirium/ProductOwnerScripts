#!/usr/bin/env python3
"""
My Tickets Report
Refactored version using JiraReportBase - reports tickets assigned to the current user.
"""

from jira_report_base import JiraReportBase, JiraUtilities, ReportConfig


class MyTicketsReport(JiraReportBase):
    """Report for tickets assigned to the current user."""
    
    def __init__(self, config_file: str = 'config.ini'):
        """Initialize the my tickets report."""
        super().__init__(config_file)
        self.projects = ['DI', 'CCS']  # Projects to check
        self.boards_info = [
            {'project': 'DI', 'board_id': 705, 'name': 'DI Board'},
            {'project': 'CCS', 'board_id': None, 'name': 'CCS Project'}
        ]
    
    def build_jql_query(self) -> str:
        """Build JQL query for tickets assigned to current user across all projects."""
        # Build query for all projects
        project_clause = " OR ".join([f"project = {project}" for project in self.projects])
        
        return f'({project_clause}) AND assignee = currentUser() ORDER BY updated DESC'
    
    def get_required_fields(self) -> list:
        """Get required fields for my tickets report."""
        return ["summary", "status", "priority", "created", "updated", "reporter"]
    
    def process_issues(self, issues: list) -> list:
        """Process raw issues into my tickets report format."""
        processed_data = []
        
        for issue in issues:
            reporter = JiraUtilities.extract_field_value(issue, 'fields.reporter')
            reporter_name = reporter.get('displayName', 'Unknown') if isinstance(reporter, dict) else 'Unknown'
            
            priority = JiraUtilities.extract_field_value(issue, 'fields.priority')
            priority_name = priority.get('name', 'None') if isinstance(priority, dict) else 'None'
            
            created_raw = JiraUtilities.extract_field_value(issue, 'fields.created')
            updated_raw = JiraUtilities.extract_field_value(issue, 'fields.updated')
            
            processed_item = {
                'Key': issue.get('key', 'N/A'),
                'Summary': JiraUtilities.extract_field_value(issue, 'fields.summary'),
                'Status': JiraUtilities.safe_get_status(issue),
                'Priority': priority_name,
                'Reporter': reporter_name,
                'Created': JiraUtilities.format_jira_date(created_raw),
                'Last Updated': JiraUtilities.format_jira_date(updated_raw),
                'URL': self.get_issue_url(issue.get('key', ''))
            }
            processed_data.append(processed_item)
        
        return processed_data
    
    def get_csv_headers(self) -> list:
        """Get CSV headers for my tickets report."""
        return ['Key', 'Summary', 'Status', 'Priority', 'Reporter', 'Created', 'Last Updated', 'URL']
    
    def get_output_filename(self) -> str:
        """Get output filename for my tickets report."""
        return str(ReportConfig.OUTPUT_DIR / "my_assigned_tickets.csv")
    
    def display_results(self, processed_data: list) -> None:
        """Display results with detailed formatting by project."""
        print(f"\n📋 My Assigned Tickets Report")
        print("=" * 80)
        
        if not processed_data:
            print("🎉 No tickets currently assigned to you!")
            return
        
        # Group by project for display
        project_groups = {}
        for item in processed_data:
            project = item['Key'].split('-')[0]  # Extract project from ticket key
            if project not in project_groups:
                project_groups[project] = []
            project_groups[project].append(item)
        
        total_tickets = 0
        
        for board_info in self.boards_info:
            project = board_info['project']
            board_name = board_info['name']
            board_id = board_info.get('board_id')
            
            project_tickets = project_groups.get(project, [])
            
            board_ref = f"Board ID: {board_id}" if board_id else "Project"
            print(f"\n🔍 {board_name} (Project: {project}, {board_ref})")
            print("-" * 80)
            
            if project_tickets:
                print(f"Found {len(project_tickets)} ticket(s) assigned to you:")
                
                for item in project_tickets:
                    print(f"\n  🎫 {item['Key']}: {item['Summary']}")
                    print(f"     Status: {item['Status']}")
                    print(f"     Priority: {item['Priority']}")
                    print(f"     Reporter: {item['Reporter']}")
                    print(f"     Last Updated: {item['Last Updated']}")
                    print(f"     URL: {item['URL']}")
                
                total_tickets += len(project_tickets)
            else:
                print("✅ No tickets assigned to you.")
        
        print("\n" + "=" * 80)
        print(f"📊 Total tickets assigned to you across all boards: {total_tickets}")
        print("=" * 80)


def main():
    """Main function to run the my tickets report."""
    report = MyTicketsReport()
    report.run_report()


if __name__ == "__main__":
    main()