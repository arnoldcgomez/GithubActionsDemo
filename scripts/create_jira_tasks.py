import sys
import pandas as pd
from jira import JIRA
import os

def main(file_path):
    jira_server = os.getenv("JIRA_DOMAIN")
    jira_user = os.getenv("JIRA_USERNAME")
    jira_api_token = os.getenv("JIRA_API_TOKEN")
    jira_project_key = os.getenv("JIRA_PROJECT_KEY")

    jira = JIRA(server=jira_server, basic_auth=(jira_user, jira_api_token))

    try:
        tasks = pd.read_excel(file_path)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        sys.exit(1)

    required_columns = ["Summary", "Description", "Issue Type", "Parent Key"]
    if not all(column in tasks.columns for column in required_columns):
        print(f"Excel must contain the following columns: {', '.join(required_columns)}")
        sys.exit(1)

    # Dictionary to store created issues by their Summary for lookup
    created_issues = {}

    # First Pass: Create all issues
    for _, row in tasks.iterrows():
        issue_data = {
            "project": {"key": jira_project_key},
            "summary": row["Summary"],
            "description": row["Description"],
            "issuetype": {"name": row["Issue Type"]},
        }

        try:
            # Create the issue in JIRA
            issue = jira.create_issue(fields=issue_data)
            print(f"Created issue {issue.key} ({row['Summary']})")
            created_issues[row["Summary"]] = issue
        except Exception as e:
            print(f"Failed to create issue for row {_}: {e}")

    # Second Pass: Link issues with their parents
    for _, row in tasks.iterrows():
        parent_key = row.get("Parent Key")
        if pd.notna(parent_key):
            # Retrieve parent issue
            parent_issue = created_issues.get(parent_key)
            child_issue = created_issues.get(row["Summary"])
            if parent_issue and child_issue:
                try:
                    if row["Issue Type"] == "Sub-task":
                        # Add parent link for Sub-task
                        jira.assign_issue(child_issue, {"parent": {"key": parent_issue.key}})
                        print(f"Linked {child_issue.key} as a Sub-task of {parent_issue.key}")
                    else:
                        print(f"Warning: Unsupported parent-child link for {row['Summary']}.")
                except Exception as e:
                    print(f"Failed to link {row['Summary']} with parent {parent_key}: {e}")
            else:
                print(f"Parent or child issue not found for {row['Summary']}. Skipping.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_jira_tasks.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    main(file_path)
