import sys
import pandas as pd
from jira import JIRA
import os

def main(file_path):
    jira_server = os.getenv("JIRA_DOMAIN")
    jira_user = os.getenv("JIRA_USERNAME")
    jira_api_token = os.getenv("JIRA_API_TOKEN")
    jira_project_key = os.getenv("JIRA_PROJECT_ID")

    print("Inside main function")
    print(f"Using Jira project key: {jira_project_key}")

    jira = JIRA(server=jira_server, basic_auth=(jira_user,jira_api_token))

    try:
      tasks = pd.read_excel(file_path)
    except Exception as e:
      print(f"Error reading Excel file: {e}")
      sys.exit(1)

    required_columns = ["Summary", "Description", "Issue Type"]
    if not all(column in tasks.columns for column in required_columns):
      print(f"Excel must contain the following columns: {', '.join(required_columns)}")

    for _, row in tasks.iterrows():
        issue_data = {
            "project": {"key": jira_project_key},
            "summary": row["Summary"],
            "description": row["Description"],
            "issuetype": {"name": row["Issue Type"]}
        }

        try:
            issue = jira.create_issue(fields = issue_data)
            print(f"Created issue {issue.key}")
        except Exception as e:
            print(f"Failed to create issue for row {_}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_jira_tasks.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    main(file_path)
