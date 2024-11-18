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

    # Setting up the API endpoints and headers
    url = f"{jira_domain}/rest/api/3/search"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # Setting up JQL
    query = {
        "jql": "project = 10000",
        "fields": ["issuetype", "project", "description"]
    }
    try:
        # Make the API Request
        response = requests.get(url, headers=headers, params=query, auth=requests.auth.HTTPBasicAuth(username, api_token))

        # Process response
        if response.status_code == 200:
            tasks = response.json()
            filtered_issues = []

            # Extract required fields
            for issue in tasks.get('issues', []):
                filtered_data = {
                    "key": issue["key"],
                    "issuetype": issue["fields"].get("issuetype"),
                    "project": issue["fields"].get("project"),
                    "description": issue["fields"].get("description")
                }
                filtered_issues.append(filtered_data)

            output_file = "filtered_jira_tasks.json"
            with open(output_file, "w") as json_file:
                json.dump({"issues": filtered_issues}, json_file, indent=4)
                print(f"Filtered data saved to {output_file}")
                print(json.dumps(filtered_issues, indent=4))

        else:
            print("Failed to fetch data:", response.status_code, response.text)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
