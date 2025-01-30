from github import Github
from datetime import datetime, timedelta
from collections import defaultdict
from github.GithubException import GithubException

def get_github_stats(token):
    # Initialize the GitHub object with the token
    g = Github(token)
    
    # Get the authenticated user
    user = g.get_user()
    
    # Get the number of repositories the user has
    repo_count = user.get_repos().totalCount
    
    # Get the number of starred repositories
    starred_count = user.get_starred().totalCount
    
    # Get the number of followers and following
    followers_count = user.followers
    following_count = user.following
    
    # Get the number of organizations the user is part of
    orgs_count = user.get_orgs().totalCount
    
    # Get the number of issues created by the user
    issues_count = user.get_issues().totalCount
    
    # Get the number of gists created by the user
    gists_count = user.get_gists().totalCount
    
    # Additional metrics for repositories
    total_commits = 0
    total_reviews = 0
    total_pull_requests = 0
    repo_activity = defaultdict(lambda: {"commits": 0, "reviews": 0, "pull_requests": 0})
    
    # Get the current date and calculate the date 30 days ago
    now = datetime.now()
    thirty_days_ago = now - timedelta(days=30)
    
    # Iterate through all repositories
    for repo in user.get_repos():
        try:
            # Get commits in the last 30 days
            commits = repo.get_commits(since=thirty_days_ago)
            commit_count = commits.totalCount
            total_commits += commit_count
            repo_activity[repo.name]["commits"] = commit_count
        except GithubException as e:
            if e.status == 409 and "Git Repository is empty" in e.data.get("message", ""):
                # Skip empty repositories
                print(f"Skipping empty repository: {repo.name}")
                continue
            else:
                # Re-raise the exception if it's not about an empty repository
                raise e
        
        # Get pull requests in the last 30 days
        pull_requests = repo.get_pulls(state="all", sort="created", direction="desc")
        for pr in pull_requests:
            # Make thirty_days_ago timezone-aware using the same timezone as pr.created_at
            thirty_days_ago_aware = thirty_days_ago.replace(tzinfo=pr.created_at.tzinfo)
            if pr.created_at >= thirty_days_ago_aware:
                total_pull_requests += 1
                repo_activity[repo.name]["pull_requests"] += 1
                
                # Get reviews for the pull request
                reviews = pr.get_reviews()
                review_count = reviews.totalCount
                total_reviews += review_count
                repo_activity[repo.name]["reviews"] += review_count
    
    # Calculate average monthly commits and reviews
    avg_monthly_commits = total_commits / 30
    avg_monthly_reviews = total_reviews / 30
    avg_monthly_pull_requests = total_pull_requests / 30
    
    # Print the statistics
    print(f"Number of repositories: {repo_count}")
    print(f"Number of starred repositories: {starred_count}")
    print(f"Number of followers: {followers_count}")
    print(f"Number of following: {following_count}")
    print(f"Number of organizations: {orgs_count}")
    print(f"Number of issues created: {issues_count}")
    print(f"Number of gists created: {gists_count}")
    print(f"Total commits in the last 30 days: {total_commits}")
    print(f"Total pull requests in the last 30 days: {total_pull_requests}")
    print(f"Total reviews in the last 30 days: {total_reviews}")
    print(f"Average monthly commits: {avg_monthly_commits:.2f}")
    print(f"Average monthly pull requests: {avg_monthly_pull_requests:.2f}")
    print(f"Average monthly reviews: {avg_monthly_reviews:.2f}")
    
    # Print repository-specific activity
    print("\nRepository Activity (last 30 days):")
    for repo_name, activity in repo_activity.items():
        print(f"{repo_name}: {activity['commits']} commits, {activity['pull_requests']} pull requests, {activity['reviews']} reviews")

if __name__ == "__main__":
    # Replace 'your_github_token' with your actual GitHub token
    github_token = "token"
    
    # Call the function to get GitHub stats
    get_github_stats(github_token)