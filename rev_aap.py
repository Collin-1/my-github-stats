import requests
from datetime import datetime
import time

# Replace with your GitHub token
GITHUB_TOKEN = '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'

# Define the date range (YYYY-MM-DD format)
START_DATE = '2024-04-01'
END_DATE = '2024-12-18'

# Convert dates to ISO format
start_date_iso = datetime.strptime(START_DATE, '%Y-%m-%d').isoformat() + 'Z'
end_date_iso = datetime.strptime(END_DATE, '%Y-%m-%d').isoformat() + 'Z'

# GitHub API base URL
BASE_URL = 'https://api.github.com'

# Headers for authentication
headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

def fetch_with_retry(url, headers, max_retries=5, delay=4, **kwargs):
    """
    Fetches data from the given URL with retry logic.
    Retries up to `max_retries` times with a delay of `delay` seconds between retries.
    Accepts additional keyword arguments for `requests.get`.
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, **kwargs)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response
        except requests.exceptions.SSLError as e:
            print(f"Attempt {attempt + 1} failed with SSLError: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Max retries reached. Skipping this request.")
                raise
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Max retries reached. Skipping this request.")
                raise
    return None

def get_all_reviews():
    cnt = 0
    # Fetch all repositories the token has access to
    repos_url = f'{BASE_URL}/user/repos'
    repos_response = fetch_with_retry(repos_url, headers)
    
    if repos_response is None:
        print("Failed to fetch repositories after retries.")
        return
    
    repositories = repos_response.json()
    
    # Iterate through each repository
    for repo in repositories:
        repo_name = repo['full_name']
        print(f"Fetching reviews for repository: {repo_name}")
        
        # Fetch all pull requests in the repository
        prs_url = f'{BASE_URL}/repos/{repo_name}/pulls'
        prs_response = fetch_with_retry(prs_url, headers, params={'state': 'all', 'per_page': 100})
        
        if prs_response is None:
            print(f"Failed to fetch pull requests for {repo_name} after retries.")
            continue
        
        pull_requests = prs_response.json()
        
        # Iterate through each pull request
        for pr in pull_requests:
            pr_number = pr['number']
            pr_title = pr['title']
            pr_url = pr['html_url']
            
            # Fetch all reviews for the pull request
            reviews_url = f'{BASE_URL}/repos/{repo_name}/pulls/{pr_number}/reviews'
            reviews_response = fetch_with_retry(reviews_url, headers)
            
            if reviews_response is None:
                print(f"Failed to fetch reviews for PR #{pr_number} in {repo_name} after retries.")
                continue
            
            reviews = reviews_response.json()
            
            # Filter reviews within the date range
            for review in reviews:
                cnt += 1
                # submitted_at = review.get('submitted_at')
                # if submitted_at and start_date_iso <= submitted_at <= end_date_iso:
                #     print(f"Repository: {repo_name}")
                #     print(f"PR Title: {pr_title}")
                #     print(f"PR URL: {pr_url}")
                #     print(f"Review submitted on: {submitted_at}")
                #     print(f"Review State: {review['state']}")
                #     print(f"Review Body: {review.get('body', 'No body provided')}")
                #     print("-" * 50)
    print(cnt)

# Run the function to get all reviews
get_all_reviews()