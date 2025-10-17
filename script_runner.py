#!/usr/bin/env python3
"""
Product Owner Scripts Runner
A wrapper script that allows you to choose and run any of the available Python scripts.
"""

import os
import sys
import subprocess
from pathlib import Path


class ScriptRunner:
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.available_scripts = self._discover_scripts()
    
    def _discover_scripts(self):
        """Discover all Python scripts in the current directory."""
        scripts = {}
        
        # Define script descriptions
        script_descriptions = {
            'da_tickets_status_changed_in_sprint.py': 'DA Tickets Status Changed in Sprint - Find tickets with status changes in the last sprint',
            'my_tickets_report.py': 'My Tickets Report - Get tickets assigned to current user from DI and CCS boards',
            'stale_tickets_report.py': 'Stale Tickets Report - Find tickets with no status change in the last 3 months (FDA/FDP boards)',
            'tempo_timesheet_analyzer.py': 'Tempo Timesheet Analyzer - Analyze Tempo timesheet data and generate reports',
            'test_sample_data.py': 'Test Sample Data - Test script with sample data'
        }
        
        # Look for Python scripts in the current directory
        for file_path in self.script_dir.glob('*.py'):
            filename = file_path.name
            
            # Skip this runner script itself
            if filename == 'script_runner.py':
                continue
                
            # Check if the file has a main function or can be run as a script
            if filename in script_descriptions:
                scripts[filename] = {
                    'path': file_path,
                    'description': script_descriptions[filename]
                }
            else:
                # Generic description for unknown scripts
                scripts[filename] = {
                    'path': file_path,
                    'description': f'Python script: {filename}'
                }
        
        return scripts
    
    def display_menu(self):
        """Display the menu of available scripts."""
        print("\n" + "="*80)
        print("🐍 PRODUCT OWNER SCRIPTS RUNNER")
        print("="*80)
        print("Available scripts:\n")
        
        for i, (filename, info) in enumerate(self.available_scripts.items(), 1):
            print(f"{i:2d}. {filename}")
            print(f"     📝 {info['description']}\n")
        
        print(f"{len(self.available_scripts) + 1:2d}. Exit")
        print("="*80)
    
    def get_user_choice(self):
        """Get user's choice from the menu."""
        max_choice = len(self.available_scripts) + 1
        
        while True:
            try:
                choice = input(f"\nEnter your choice (1-{max_choice}): ").strip()
                
                if not choice:
                    continue
                    
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(self.available_scripts):
                    return choice_num
                elif choice_num == max_choice:
                    return -1  # Exit
                else:
                    print(f"❌ Invalid choice. Please enter a number between 1 and {max_choice}")
                    
            except ValueError:
                print("❌ Invalid input. Please enter a number.")
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                return -1
    
    def run_script(self, script_path):
        """Run the selected script."""
        try:
            print(f"\n🚀 Running: {script_path.name}")
            print("-" * 50)
            
            # Change to script directory to ensure relative paths work
            original_dir = os.getcwd()
            os.chdir(self.script_dir)
            
            # Run the script
            result = subprocess.run([sys.executable, str(script_path)], 
                                  capture_output=False, 
                                  text=True)
            
            # Restore original directory
            os.chdir(original_dir)
            
            print("-" * 50)
            if result.returncode == 0:
                print("✅ Script completed successfully!")
            else:
                print(f"❌ Script exited with code: {result.returncode}")
                
        except Exception as e:
            print(f"❌ Error running script: {e}")
        finally:
            # Restore original directory in case of exception
            if 'original_dir' in locals():
                os.chdir(original_dir)
    
    def run(self):
        """Main runner loop."""
        if not self.available_scripts:
            print("❌ No Python scripts found in the current directory.")
            return
        
        try:
            while True:
                self.display_menu()
                choice = self.get_user_choice()
                
                if choice == -1:
                    print("\n👋 Goodbye!")
                    break
                
                # Get the selected script
                script_items = list(self.available_scripts.items())
                selected_filename, script_info = script_items[choice - 1]
                
                print(f"\n📋 Selected: {script_info['description']}")
                
                # Confirm before running
                confirm = input("\nDo you want to run this script? (y/N): ").strip().lower()
                if confirm in ['y', 'yes']:
                    self.run_script(script_info['path'])
                    
                    # Ask if user wants to run another script
                    again = input("\nWould you like to run another script? (Y/n): ").strip().lower()
                    if again in ['n', 'no']:
                        print("\n👋 Goodbye!")
                        break
                else:
                    print("❌ Script execution cancelled.")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")


def main():
    """Main entry point."""
    runner = ScriptRunner()
    runner.run()


if __name__ == "__main__":
    main()