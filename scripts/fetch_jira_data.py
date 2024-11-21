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

    # Setting up the API endpoint and headers for fetching projects
    projects_url = f"{jira_domain}/rest/api/3/project"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    all_filtered_issues = []

    try:
        # Get all projects
        project_response = requests.get(projects_url, headers=headers, auth=requests.auth.HTTPBasicAuth(username, api_token))

        # Check for successful project retrieval
        if project_response.status_code == 200:
            projects = project_response.json()
            project_keys = [project["id"] for project in projects]  # Extract all project keys
            
            print(f"Found project keys: {project_keys}")

            # Setting up the API endpoint for issues
            issues_url = f"{jira_domain}/rest/api/3/search"

            # Loop through each project key and fetch issues
            for project_key in project_keys:
                print(f"Fetching issues for project: {project_key}")

                # Setting up JQL for each project
                query = {
                    "jql": f"project = {project_key}",
                    "fields": ["issuetype", "project", "assignee", "description"]
                }

                # Make the API request for each project
                response = requests.get(issues_url, headers=headers, params=query, auth=requests.auth.HTTPBasicAuth(username, api_token))

                # Process response
                if response.status_code == 200:
                    tasks = response.json()
                    filtered_issues = []

                    # Extract required fields
                    for issue in tasks.get('issues', []):
                        filtered_data = {
                            "id": issue["id"],
                            "key": issue["key"],
                            "issuetype": issue["fields"].get("issuetype"),
                            "project": issue["fields"].get("project"),
                            "assignee": issue["fields"].get("assignee"),
                            "description": issue["fields"].get("description")
                        }
                        filtered_issues.append(filtered_data)

                    # Append fetched issues to the all_filtered_issues list
                    all_filtered_issues.extend(filtered_issues)

                    print(f"Fetched {len(filtered_issues)} issues for project: {project_key}")

                else:
                    print(f"Failed to fetch data for project {project_key}:", response.status_code, response.text)

            # Save all issues to a single output file
            output_file = "filtered_jira_tasks.json"
            with open(output_file, "w") as json_file:
                json.dump({"issues": all_filtered_issues}, json_file, indent=4)

            print(f"Filtered data for all projects saved to {output_file}")
            print(json.dumps(all_filtered_issues, indent=4))

        else:
            print("Failed to fetch projects:", project_response.status_code, project_response.text)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
