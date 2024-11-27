import os
import requests
import json

def main():
    # Loading the Env Variables
    jira_domain = os.getenv("JIRA_DOMAIN")
    api_token = os.getenv("JIRA_API_TOKEN")
    username = os.getenv("JIRA_USERNAME")

    # Validate environment variables
    if not jira_domain or not api_token or not username:
        print("Error: Missing required environment variables")
        return

    # Input Task ID
    task_id = input("Enter the Jira Task ID: ").strip()
    if not task_id:
        print("Error: Task ID cannot be empty")
        return

    # Setting up the API endpoint and headers
    url = f"{jira_domain}/rest/api/3/issue/{task_id}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    try:
        # Make the API Request
        response = requests.get(url, headers=headers, auth=requests.auth.HTTPBasicAuth(username, api_token))

        # Process response
        if response.status_code == 200:
            issue = response.json()

            # Extract required fields
            filtered_data = {
                "id": issue.get("id"),
                "key": issue.get("key"),
                "issuetype": issue["fields"].get("issuetype"),
                "project": issue["fields"].get("project"),
                "assignee": issue["fields"].get("assignee"),
                "description": issue["fields"].get("description")
            }

            output_file = f"jira_task_{task_id}.json"
            with open(output_file, "w") as json_file:
                json.dump(filtered_data, json_file, indent=4)
                print(f"Task data saved to {output_file}")
                print(json.dumps(filtered_data, indent=4))

        else:
            print("Failed to fetch data:", response.status_code, response.text)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
