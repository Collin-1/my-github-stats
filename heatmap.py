import requests
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def get_github_contributions(github_token, username):
    url = 'https://api.github.com/graphql'

    query = """
    query($username: String!, $from: DateTime!, $to: DateTime!) {
    user(login: $username) {
        contributionsCollection(from: $from, to: $to) {
        contributionCalendar {
            totalContributions
            weeks {
            contributionDays {
                contributionCount
                date
                weekday
            }
            }
        }
        }
    }
    }
    """

    # Calculate date range from last April to now
    end_date = datetime.now()
    current_year = end_date.year
    start_year = current_year - 1 if end_date.month < 4 else current_year
    start_date = datetime(start_year, 4, 1)  # April 1st of the previous year

    variables = {
        "username": username,
        "from": start_date.isoformat(),
        "to": end_date.isoformat()
    }

    headers = {
        "Authorization": f"Bearer {github_token}",
        "Content-Type": "application/json",
    }

    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
    return response.json()

def create_contribution_heatmap(github_token, username):
    # Fetch contribution data
    data = get_github_contributions(github_token, username)

    # Process the data
    contributions = []
    dates = []
    weeks = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']

    for week in weeks:
        for day in week['contributionDays']:
            contributions.append(day['contributionCount'])
            dates.append(datetime.strptime(day['date'], '%Y-%m-%d'))

    # Create a DataFrame
    df = pd.DataFrame({
        'date': dates,
        'contributions': contributions
    })

    # Create the calendar heatmap
    df['weekday'] = df['date'].dt.weekday
    df['week'] = df['date'].dt.isocalendar().week
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year

    # Create unique week identifier to handle year transition
    df['week_id'] = (df['date'] - df['date'].min()).dt.days // 7

    # Create pivot table
    pivot_data = df.pivot_table(
        values='contributions',
        index='weekday',
        columns='week_id',
        fill_value=0
    )

    # Add spacing between months
    new_data = []
    month_labels = []
    month_positions = []
    current_month = None
    current_pos = 0

    for week_id in pivot_data.columns:
        week_dates = df[df['week_id'] == week_id]['date']
        month = week_dates.iloc[0].month if len(week_dates) > 0 else None
        year = week_dates.iloc[0].year if len(week_dates) > 0 else None
        
        if month != current_month and current_month is not None:
            # Add a column of zeros for spacing
            new_data.append(np.zeros(7))
            current_pos += 1
            month_labels.append('')
            month_positions.append(current_pos - 0.5)
            
        new_data.append(pivot_data[week_id].values)
        current_pos += 1
        
        if month != current_month:
            current_month = month
            # Add year to month label if it's January
            month_label = week_dates.iloc[0].strftime('%B')
            if month == 1:
                month_label += f"\n{year}"
            month_labels.append(month_label)
            month_positions.append(current_pos - 0.5)

    # Calculate total contributions
    total_contributions = df['contributions'].sum()

    # Create the heatmap using plotly
    fig = go.Figure(data=go.Heatmap(
        z=np.transpose(new_data),
        colorscale=[
            [0, 'rgb(255,245,245)'],  # lightest red
            [0.2, 'rgb(254,224,210)'],
            [0.4, 'rgb(252,187,161)'],
            [0.6, 'rgb(252,146,114)'],
            [0.8, 'rgb(251,106,74)'],
            [1, 'rgb(203,24,29)']     # darkest red
        ],
        showscale=True,
        xgap=1,
        ygap=1,
    ))

    # Update layout
    fig.update_layout(
    title=f'GitHub Contributions Heatmap for {username}<br>Total Contributions: {total_contributions}',
    xaxis_title='',
    yaxis_title='',
    xaxis=dict(
        ticktext=month_labels,
        tickvals=month_positions,
        tickangle=0,
        side='top'
    ),
    yaxis=dict(
        ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        tickvals=[0, 1, 2, 3, 4, 5, 6],
    ),
    height=300,
    paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
    plot_bgcolor='rgba(0,0,0,0)'    # Transparent plot area
    )

    return fig

# Usage example
if __name__ == "__main__":
    # Replace with your GitHub personal access token and username
    github_token = "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"
    username = "Collin-1"

    fig = create_contribution_heatmap(github_token, username)
    fig.show()