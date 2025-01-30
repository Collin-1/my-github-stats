import requests
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import MonthLocator, DateFormatter
from datetime import datetime
import seaborn as sns
import time


def get_commit_stats(owner, repo, token, max_retries=5, delay=4):
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    url = f'https://api.github.com/repos/{owner}/{repo}/stats/code_frequency'

    for attempt in range(max_retries):
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 202:
            print(f"GitHub is calculating statistics for {repo}... Attempt {attempt + 1}/{max_retries}")
            time.sleep(delay)
        else:
            print(f"Error fetching {repo}: {response.status_code}")
            return None

    print(f"Max retries reached for {repo}. Please try again later.")
    return None

def combine_repo_stats(repos_data, start_date='2024-04-01', end_date=None):
    """Combine statistics from multiple repositories with date range filtering"""
    all_stats = []

    # Convert dates to pandas datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date) if end_date else pd.Timestamp.now()

    for owner, repo, stats in repos_data:
        if stats:
            df = pd.DataFrame(stats, columns=['date', 'additions', 'deletions'])
            df['repo'] = repo
            df['date'] = pd.to_datetime(df['date'], unit='s')
            
            # Filter data between start and end dates
            df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
            
            if not df.empty:
                all_stats.append(df)

    if not all_stats:
        return None, None

    # Combine all repository data
    combined_df = pd.concat(all_stats, ignore_index=True)

    # Group by date and sum the statistics
    daily_stats = combined_df.groupby('date').agg({
        'additions': 'sum',
        'deletions': 'sum'
    }).reset_index()

    return daily_stats, combined_df

def create_visualizations(daily_stats, combined_df, repo_names, start_date, end_date):
    if daily_stats is None or daily_stats.empty:
        print("No data to visualize in the specified date range")
        return
        
    # Calculate cumulative lines of code
    daily_stats['net_changes'] = daily_stats['additions'] + daily_stats['deletions']
    daily_stats['cumulative_loc'] = daily_stats['net_changes'].cumsum()

    # Format date range for title
    start_str = pd.to_datetime(start_date).strftime('%Y-%m-%d')
    end_str = pd.to_datetime(end_date).strftime('%Y-%m-%d')
    base_title = f'Combined Code Statistics for {len(repo_names)} Repositories\n({start_str} to {end_str})'

    # 1. Total Lines of Code
    fig1 = plt.figure(figsize=(12, 6), facecolor='none', edgecolor='none')
    ax1 = fig1.add_subplot(111)
    ax1.plot(daily_stats['date'], daily_stats['cumulative_loc'], color='blue', linewidth=2)
    ax1.set_title('Total Lines of Code Over Time\n')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Lines of Code')
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.xaxis.set_major_locator(MonthLocator())
    ax1.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)
    ax1.set_facecolor('none')
    plt.tight_layout()
    plt.savefig('total_lines.png', transparent=True, bbox_inches='tight')
    plt.show()

    # 2. Cumulative Growth Line Chart
    fig2 = plt.figure(figsize=(12, 6), facecolor='none', edgecolor='none')
    ax2 = fig2.add_subplot(111)
    ax2.plot(daily_stats['date'], daily_stats['cumulative_loc'], color='green', linewidth=2)
    ax2.set_title('Cumulative Code Growth\n')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Cumulative Lines of Code')
    ax2.fill_between(daily_stats['date'], daily_stats['cumulative_loc'], alpha=0.3, color='red')
    ax2.grid(True, linestyle='--', alpha=0.7)
    ax2.xaxis.set_major_locator(MonthLocator())
    ax2.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)
    ax2.set_facecolor('none')
    plt.tight_layout()
    plt.savefig('cumulative_growth.png', transparent=True, bbox_inches='tight')
    plt.show()

    # 3. Additions vs Deletions Bar Chart
    fig3 = plt.figure(figsize=(12, 6), facecolor='none', edgecolor='none')
    ax3 = fig3.add_subplot(111)
    width = 0.35
    ax3.bar(daily_stats['date'], daily_stats['additions'], width, label='Additions', color='green', alpha=0.6)
    ax3.bar(daily_stats['date'], daily_stats['deletions'], width, label='Deletions', color='red', alpha=0.6)
    ax3.set_title('Monthly Code Additions vs Deletions\n')
    ax3.set_xlabel('Date')
    ax3.set_ylabel('Lines of Code')
    ax3.legend()
    ax3.grid(True, linestyle='--', alpha=0.7)
    ax3.xaxis.set_major_locator(MonthLocator())
    ax3.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)
    ax3.set_facecolor('none')
    plt.tight_layout()
    plt.savefig('additions_deletions.png', transparent=True, bbox_inches='tight')
    plt.show()

    # Print statistics
    print(f"\nCombined Repository Statistics ({start_str} to {end_str}):")
    print("-" * 50)
    print(f"Total Lines of Code: {daily_stats['cumulative_loc'].iloc[-1]:,.0f}")
    print(f"Total Additions: {daily_stats['additions'].sum():,.0f}")
    print(f"Total Deletions: {abs(daily_stats['deletions'].sum()):,.0f}")
    print(f"Average Weekly Additions: {daily_stats['additions'].mean():,.0f}")
    print(f"Average Weekly Deletions: {abs(daily_stats['deletions'].mean()):,.0f}")

    # Per-repository statistics
    print(f"\nPer-Repository Statistics ({start_str} to {end_str}):")
    print("-" * 50)
    for repo in repo_names:
        repo_data = combined_df[combined_df['repo'] == repo]
        if not repo_data.empty:
            total_additions = repo_data['additions'].sum()
            total_deletions = abs(repo_data['deletions'].sum())
            print(f"\n{repo}:")
            print(f"Total Additions: {total_additions:,.0f}")
            print(f"Total Deletions: {total_deletions:,.0f}")
        print(f"Net Changes: {total_additions + total_deletions:,.0f}")

def main():
    # Define date range
    start_date = '2024-04-01'
    end_date = '2024-12-18'  # Set to None for current date

    token = "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"
    OWNER = "Umuzi-org"

    repositories = [
            (OWNER , "Collin-Makwala-186-consume-github-api-python"),
            (OWNER , "Collin-Makwala-959-contentitem-python"),
            (OWNER ,"Collin-Makwala-952-contentitem-python"),
            (OWNER ,"Collin-Makwala-705-contentitem-python"),
            (OWNER ,"Collin-Makwala-200-sql-"),
            (OWNER ,"Collin-Makwala-266-string-calculator-python"),
            (OWNER ,"Collin-Makwala-247-data-wrangling-python"), 
            (OWNER ,"Collin-Makwala-256-python-and-mongodb-python"),
            (OWNER ,"Collin-Makwala-190-rabbitmq-python"),
            (OWNER ,"Collin-Makwala-263-create-a-rest-api-to-interact-with-actual-database-python"),
            (OWNER ,"Collin-Makwala-261-database-migrations-with-sqlalchemy-python"),
            (OWNER ,"Collin-Makwala-958-contentitem-python"),
            (OWNER ,"Collin-1.github.io")
        ]

    # Fetch stats for all repositories
    repos_data = []
    for owner, repo in repositories:
        print(f"Fetching statistics for {owner}/{repo}...")
        stats = get_commit_stats(owner, repo, token, max_retries=5)
        if stats:
            repos_data.append((owner, repo, stats))

    if not repos_data:
        print("No valid repository data found.")
        return

    # Combine and visualize stats with date filtering
    daily_stats, combined_df = combine_repo_stats(repos_data, start_date=start_date, end_date=end_date)
    if daily_stats is None or daily_stats.empty:
        print(f"No data available for the period {start_date} to {end_date}.")
        return
        
    repo_names = [repo for _, repo, _ in repos_data]
    create_visualizations(daily_stats, combined_df, repo_names, start_date, end_date)

if __name__ == "__main__":
    main()
