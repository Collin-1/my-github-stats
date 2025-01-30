import requests
from datetime import datetime

# Replace with your GitHub token
GITHUB_TOKEN = "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"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}
USERNAME = "Collin-1"
ORGANIZATION = "Umuzi-org"

def get_all_repos():
    url = "https://api.github.com/user/repos"
    repos = []
    page = 1
    while True:
        response = requests.get(url, headers=HEADERS, params={"page": page, "per_page": 100})
        if response.status_code != 200:
            break
        repos_page = response.json()
        if not repos_page:
            break
        repos.extend(repos_page)
        page += 1
    return repos

def get_projects():
    url = "https://api.github.com/user/projects"
    response = requests.get(url, headers=HEADERS)
    return response.json()

def get_reviews():
    url = f"https://api.github.com/search/issues?q=reviewed-by:{USERNAME}"
    response = requests.get(url, headers=HEADERS)
    return response.json()

def get_open_prs():
    url = f"https://api.github.com/search/issues?q=author:{USERNAME}+type:pr+state:open"
    response = requests.get(url, headers=HEADERS)
    return response.json()

def get_filtered_repos():
    repos = get_all_repos()
    filtered_repos = [repo["name"] for repo in repos if "Collin-Makwala" in repo['name']]
    print(len(filtered_repos))
    return filtered_repos

def filter_by_date(data, start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    return [item for item in data if 'updated_at' in item and start <= datetime.strptime(item['updated_at'], "%Y-%m-%dT%H:%M:%SZ") <= end]

def main():
    start_date = "2024-04-01"  # Replace with your start date
    end_date = "2024-12-18"    # Replace with your end date

    repos = get_all_repos()
    projects = get_projects()
    reviews = get_reviews()
    open_prs = get_open_prs()
    filtered_repos = get_filtered_repos()

    # Debugging: Print the structure of the projects data
    print("Projects data structure:", projects)

    repos = filter_by_date(repos, start_date, end_date)
    reviews['items'] = filter_by_date(reviews['items'], start_date, end_date)
    open_prs['items'] = filter_by_date(open_prs['items'], start_date, end_date)
    filtered_repos = filter_by_date(filtered_repos, start_date, end_date)

    print(f"Repositories with 'Collin-Makwala' in the name: {len(filtered_repos)}")
    print(f"Number of repositories worked on: {len(repos)}")
    print(f"Number of projects worked on: {len(projects)}")
    print(f"Number of reviews done: {reviews['total_count']}")
    print(f"Number of open PRs: {open_prs['total_count']}")
    

if __name__ == "__main__":
    main()