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

    # Dictionary to store created issues by their summary for lookup
    created_issues = {}

    # Process rows by hierarchy
    issue_types_order = ["Epic", "Story", "Sub-task"]  # Define order for processing
    for issue_type in issue_types_order:
        for _, row in tasks[tasks["Issue Type"] == issue_type].iterrows():
            issue_data = {
                "project": {"key": jira_project_key},
                "summary": row["Summary"],
                "description": row["Description"],
                "issuetype": {"name": row["Issue Type"]},
            }

            # Check if the task has a parent and set the parent field accordingly
            parent_key = row.get("Parent Key")
            if pd.notna(parent_key):
                parent_issue = created_issues.get(parent_key)
                if parent_issue:
                    if row["Issue Type"] == "Sub-task":
                        issue_data["parent"] = {"key": parent_issue.key}
                    else:
                        print(f"Warning: Invalid parent-child relation for {row['Summary']}. Skipping.")
                        continue
                else:
                    print(f"Parent issue '{parent_key}' not found for {row['Summary']}. Skipping.")
                    continue

            try:
                issue = jira.create_issue(fields=issue_data)
                print(f"Created issue {issue.key} ({row['Summary']})")
                created_issues[row["Summary"]] = issue
            except Exception as e:
                print(f"Failed to create issue for row {_}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_jira_tasks.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    main(file_path)
