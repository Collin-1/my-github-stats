import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Custom CSS for red theme
st.markdown("""
    <style>
    .css-18e3th9 {
        background-color: #ffcccc;
    }
    .css-1d391kg {
        color: #ff0000;
    }
    .css-1v3fvcr {
        color: #ff0000;
    }
    .css-1cpxqw2 {
        color: #ff0000;
    }
    .css-1v0mbdj {
        color: #ff0000;
    }
    .css-1v0mbdj h1, .css-1v0mbdj h2, .css-1v0mbdj h3, .css-1v0mbdj h4, .css-1v0mbdj h5, .css-1v0mbdj h6 {
        color: #ff0000;
    }
    </style>
""", unsafe_allow_html=True)

# Set page configuration
st.set_page_config(page_title="Data Engineering Skills", layout="wide")

# Title and Introduction
st.title("Data Engineering Skills Development")
st.markdown("### Skills acquired through 15 project implementations")

# Create columns for key metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Projects Completed", "15")
with col2:
    st.metric("Core Technologies", "4")
with col3:
    st.metric("Total Skills", "50+")
with col4:
    st.metric("Completion Rate", "100%")

# Skills data
skills_data = {
    "Category": [
        "Programming Fundamentals",
        "Data Handling",
        "Database Skills",
        "API & Integration",
        "DevOps & Tools",
        "Testing & Quality"
    ],
    "Skills": [
        ["OOP", "TDD", "Error Handling", "Clean Code", "Function Design"],
        ["File I/O", "JSON Processing", "Pandas", "Data Validation", "Data Cleaning"],
        ["SQL", "MongoDB", "Migrations", "SQLAlchemy", "Data Modeling"],
        ["REST API", "API Consumption", "HTTP Methods", "Authentication", "Integration"],
        ["Docker", "Git", "Environmental Variables", "RabbitMQ", "Airflow"],
        ["Unit Testing", "Test Coverage", "Mocking", "Assertions", "Documentation"]
    ],
    "Proficiency": [90, 85, 80, 85, 75, 85]
}

# Project complexity data
project_complexity = {
    "Project": [
        "Animals OOP",
        "Simple Calculator",
        "ID Validator",
        "File Operations",
        "Shopping Cart",
        "Pandas Helpers",
        "Data Wrangling",
        "Bank Accounts",
        "Email Quote System",
        "REST API",
        "MongoDB",
        "RabbitMQ",
        "Airflow DAGs"
    ],
    "Complexity": [1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3]
}

# Create tabs for different views
tab1, tab2, tab3 = st.tabs(["Skills Overview", "Project Progression", "Detailed Skills"])

with tab1:
    # Skills radar chart
    categories = skills_data["Category"]
    proficiency = skills_data["Proficiency"]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=proficiency,
        theta=categories,
        fill='toself',
        name='Skills Proficiency'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=False
    )

    st.plotly_chart(fig)

with tab2:
    # Project progression
    df_projects = pd.DataFrame(project_complexity)
    fig = px.bar(df_projects, 
                x='Project', 
                y='Complexity',
                color='Complexity',
                title='Project Complexity Progression')
    st.plotly_chart(fig)

with tab3:
    # Detailed skills breakdown
    for category, skills in zip(skills_data["Category"], skills_data["Skills"]):
        st.subheader(category)
        cols = st.columns(5)
        for i, skill in enumerate(skills):
            with cols[i]:
                st.markdown(f"- {skill}")

# Add skill distribution pie chart
st.subheader("Skill Distribution")
skill_distribution = {
    "Category": ["Programming", "Data", "DevOps", "Testing", "Integration"],
    "Percentage": [30, 25, 20, 15, 10]
}
fig = px.pie(values=skill_distribution["Percentage"],
         names=skill_distribution["Category"],
         title="Skill Category Distribution")
st.plotly_chart(fig)

# Project timeline
st.subheader("Project Timeline")
timeline_data = pd.DataFrame({
    "Project": project_complexity["Project"],
    "Start": pd.date_range(start="2023-01-01", periods=len(project_complexity["Project"]), freq="W"),
    "Duration": [7] * len(project_complexity["Project"])
})

fig = px.timeline(timeline_data, 
             x_start="Start", 
             x_end=timeline_data["Start"] + pd.to_timedelta(timeline_data["Duration"], "D"),
             y="Project",
             title="Project Timeline")
st.plotly_chart(fig)

# Add filters and interactivity
st.sidebar.title("Filters")
selected_category = st.sidebar.selectbox("Select Skill Category", skills_data["Category"])
selected_skills = skills_data["Skills"][skills_data["Category"].index(selected_category)]
st.sidebar.write("Skills in selected category:")
for skill in selected_skills:
    st.sidebar.markdown(f"- {skill}")