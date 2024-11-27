import os
import requests
import json

def fetch_jira_task(task_id, jira_domain, username, api_token):
    url = f"{jira_domain}/rest/api/3/issue/{task_id}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, auth=requests.auth.HTTPBasicAuth(username, api_token))
        if response.status_code == 200:
            issue = response.json()
            filtered_data = {
                "id": issue.get("id"),
                "key": issue.get("key"),
                "issuetype": issue["fields"].get("issuetype"),
                "project": issue["fields"].get("project"),
                "assignee": issue["fields"].get("assignee"),
                "description": issue["fields"].get("description")
            }
            return filtered_data
        else:
            print(f"Failed to fetch data for {task_id}: {response.status_code} {response.text}")
            return None
    except Exception as e:
        print(f"An error occurred while fetching {task_id}: {e}")
        return None

def main():
    # Load environment variables
    jira_domain = os.getenv("JIRA_DOMAIN")
    api_token = os.getenv("JIRA_API_TOKEN")
    username = os.getenv("JIRA_USERNAME")
    task_ids_env = os.getenv("JIRA_TASK_IDS")  # Comma-separated task IDs

    # Validate environment variables
    if not jira_domain or not api_token or not username or not task_ids_env:
        print("Error: Missing required environment variables")
        return

    # Parse task IDs from environment variable
    task_ids = [task_id.strip() for task_id in task_ids_env.split(",")]

    # Fetch data for each task ID
    all_tasks = []
    for task_id in task_ids:
        print(f"Fetching data for Task ID: {task_id}")
        task_data = fetch_jira_task(task_id, jira_domain, username, api_token)
        if task_data:
            all_tasks.append(task_data)
            # Save individual JSON file for each task
            output_file = f"jira_task_{task_id}.json"
            with open(output_file, "w") as json_file:
                json.dump(task_data, json_file, indent=4)

    # Save all tasks to a combined JSON file
    combined_output = "all_jira_tasks.json"
    with open(combined_output, "w") as json_file:
        json.dump({"tasks": all_tasks}, json_file, indent=4)
        print(f"All tasks data saved to {combined_output}")

if __name__ == "__main__":
    main()
