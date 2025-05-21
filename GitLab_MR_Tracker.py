import streamlit as st
import requests
from datetime import datetime, timedelta, timezone
import json
import time
import pandas as pd
import io
import logging
import traceback

# Set page config - hide default header and footer
st.set_page_config(
    page_title="GitLab MR Tracker",
    page_icon=":rocket:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Report a bug': None,
        'About': None
    }
)

logging.basicConfig(level=logging.ERROR, filename='error.log')

# Hide default Streamlit header and footer
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Custom CSS for modern styling
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    .header {
        color: #2c3e50;
        padding: 1rem;
        border-radius: 0.5rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    .project-card {
        background: white;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s;
    }
    .project-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .projects-container {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    .section-divider {
        margin: 3rem 0;
    }
    .tag-badge {
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 0.25rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.85rem;
        font-weight: 500;
        display: inline-block;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .mr-item {
        padding: 0.75rem;
        margin-bottom: 0.75rem;
        background-color: #f8f9fa;
        border-left: 3px solid #4285f4;
        border-radius: 0.25rem;
    }
    .stButton>button {
        background-color: #4285f4;
        color: white;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #3367d6;
        color: white;
    }
    .stDateInput>div>div>input {
        border-radius: 0.5rem !important;
    }
    .stSelectbox>div>div>select {
        border-radius: 0.5rem !important;
    }
    .stTextInput>div>div>input {
        border-radius: 0.5rem !important;
    }
    .repo-name {
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .logout-btn {
        position: absolute;
        top: 1rem;
        right: 1rem;
    }
    .login-container {
        max-width: 600px;
        margin: 0 auto;
        padding: 2rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = ""
if 'base_url' not in st.session_state:
    st.session_state.base_url = "https://gitlab.swifttech.com.np/api/v4"
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def extract_repo_name(full_path):
    """Extract just the repository name from the full path"""
    return full_path.split('/')[-1]

def logout():
    """Clear session state"""
    st.session_state.authenticated = False
    st.session_state.token = ""
    st.session_state.base_url = "https://gitlab.swifttech.com.np/api/v4"
    st.rerun()

# Token configuration page
def login_page():
    with st.container():
        st.markdown("""
        <div class="login-container">
            <h1 style="text-align: center; margin-bottom: 2rem;">🔑 GitLab Login</h1>
        """, unsafe_allow_html=True)
        
        token = st.text_input("GitLab Personal Access Token", 
                            value="",
                            type="password", 
                            help="The token should have 'api' scope")
        
        base_url = st.text_input("GitLab API Base URL", 
                                value=st.session_state.base_url,
                                help="Default is your company's GitLab instance")
        
        if st.button("Login", use_container_width=True):
            if token:
                st.session_state.token = token
                st.session_state.base_url = base_url.rstrip('/')
                st.session_state.authenticated = True
                st.success("Login successful! Redirecting to dashboard...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Please enter a valid GitLab access token")
        
        st.markdown("</div>", unsafe_allow_html=True)

# Main dashboard page
def dashboard_page():
    # Header with logout button
    col1, col2 = st.columns([5, 1])
    with col1:
        st.title("🚀 GitLab Merge Request & Release Tracker")
    with col2:
        if st.button("Logout", key="logout_btn"):
            logout()
    
    st.markdown("""
    <div class="header">
        <h2 style="margin: 0;">Track merge requests and releases across your GitLab projects</h2>
        <p style="margin: 0.5rem 0 0; opacity: 0.8;">Monitor development activity and release status</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar filters
    with st.sidebar:
        st.header("🔍 Filters")
        
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=datetime.now(timezone.utc) - timedelta(days=7))
        with col2:
            end_date = st.date_input("End Date", value=datetime.now(timezone.utc))
        
        # Branch selectors
        merge_from = st.text_input("Merge From Branch", value="develop")
        merge_to = st.text_input("Merge To Branch", value="testing1.1")
        
        # Group path
        group_path = st.text_input("Group Path", value="bfi/backend", 
                                 help="The GitLab group path to analyze (e.g., 'bfi/backend')")
    
    # Convert dates to ISO format with timezone
    after = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    before = datetime.combine(end_date, datetime.max.time()).replace(tzinfo=timezone.utc)
    
    # Define API functions with caching
    @st.cache_data(ttl=300, show_spinner=False)
    def get_group_id():
        response = requests.get(
            f"{st.session_state.base_url}/groups/{group_path.replace('/', '%2F')}",
            headers={"PRIVATE-TOKEN": st.session_state.token}
        )
        response.raise_for_status()
        return response.json()["id"]
    
    @st.cache_data(ttl=300, show_spinner=False)
    def get_subgroups(group_id):
        subgroups = []
        page = 1
        while True:
            response = requests.get(
                f"{st.session_state.base_url}/groups/{group_id}/subgroups",
                headers={"PRIVATE-TOKEN": st.session_state.token},
                params={"per_page": 100, "page": page}
            )
            data = response.json()
            if not data:
                break
            subgroups.extend(data)
            page += 1
        return subgroups
    
    @st.cache_data(ttl=300, show_spinner=False)
    def get_group_projects(group_id):
        all_projects = []
        page = 1
        while True:
            response = requests.get(
                f"{st.session_state.base_url}/groups/{group_id}/projects",
                headers={"PRIVATE-TOKEN": st.session_state.token},
                params={"per_page": 100, "page": page}
            )
            data = response.json()
            if not data:
                break
            all_projects.extend(data)
            page += 1
        return all_projects
    
    @st.cache_data(ttl=300, show_spinner=False)
    def get_merged_mrs(project_id, _merge_from=merge_from, _merge_to=merge_to, _after=after.isoformat(), _before=before.isoformat()):
        url = f"{st.session_state.base_url}/projects/{project_id}/merge_requests"
        params = {
            "source_branch": _merge_from,
            "target_branch": _merge_to,
            "state": "merged",
            "updated_after": _after,
            "updated_before": _before,
            "per_page": 5  # Only get the most recent 5 MRs
        }
        response = requests.get(url, headers={"PRIVATE-TOKEN": st.session_state.token}, params=params)
        if response.status_code != 200:
            st.error(f"Failed to fetch MRs for project ID {project_id}: {response.status_code}")
            return []
        return response.json()
    
    @st.cache_data(ttl=300, show_spinner=False)
    def get_project_tags(project_id, _after=after.isoformat(), _before=before.isoformat()):
        tags = []
        page = 1
        while True:
            response = requests.get(
                f"{st.session_state.base_url}/projects/{project_id}/repository/tags",
                headers={"PRIVATE-TOKEN": st.session_state.token},
                params={"per_page": 100, "page": page}
            )
            if response.status_code != 200:
                st.error(f"Failed to fetch tags for project ID {project_id}: {response.status_code}")
                return []
            data = response.json()
            if not data:
                break
            # Ensure data is a list and each tag is valid
            if not isinstance(data, list):
                st.warning(f"Invalid tag data for project ID {project_id}: {data}")
                break
            tags.extend(data)
            page += 1
        filtered_tags = []
        for tag in tags:
            # Check if tag and commit data are valid
            if not isinstance(tag, dict) or not tag.get("commit") or not tag["commit"].get("committed_date"):
                st.warning(f"Skipping invalid tag for project ID {project_id}: {tag}")
                continue
            tag_commit_date_str = tag["commit"]["committed_date"]
            try:
                tag_commit_date = datetime.fromisoformat(tag_commit_date_str.replace("Z", "+00:00"))
                if after <= tag_commit_date <= before:
                    filtered_tags.append(tag)
            except ValueError as e:
                st.warning(f"Invalid date format for tag in project ID {project_id}: {tag_commit_date_str}")
                continue
        return filtered_tags
    
    @st.cache_data(ttl=300, show_spinner=False)
    def generate_excel(projects, merge_from, merge_to, _after=after.isoformat(), _before=before.isoformat()):
        data = []
        for project in projects:
            mrs = get_merged_mrs(project["id"], merge_from, merge_to, _after, _before)
            tags = get_project_tags(project["id"], _after, _before)
            repo_name = extract_repo_name(project['path_with_namespace'])
            
            if mrs or tags:
                tag_name = tags[0]["name"] if tags else "none"
                data.append({
                    "Repository Name": repo_name,
                    "Merged From Branch": merge_from,
                    "Merged To Branch": merge_to,
                    "Tag Name": tag_name
                })
        
        df = pd.DataFrame(data)
        df = df.sort_values(by="Repository Name")
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='GitLab Activity')
            # Adjust column widths
            worksheet = writer.sheets['GitLab Activity']
            for idx, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(idx, idx, max_len)
        return output.getvalue()
    
    def clear_all_caches():
        """Clear caches for all API functions"""
        get_group_id.clear()
        get_subgroups.clear()
        get_group_projects.clear()
        get_merged_mrs.clear()
        get_project_tags.clear()
        generate_excel.clear()
    
    # Refresh button
    with st.sidebar:
        if st.button("Refresh Data", use_container_width=True):
            clear_all_caches()
            st.rerun()
    
    def get_tag_info(project_id, tag_name):
        url = f"{st.session_state.base_url}/projects/{project_id}/repository/tags/{tag_name}"
        response = requests.get(url, headers={"PRIVATE-TOKEN": st.session_state.token})
        
        if response.status_code != 200:
            return None, None

        data = response.json()
        release = data.get("release")
        
        if isinstance(release, dict):
            description = release.get("description") or "No release description available"
        else:
            description = "No release description available"
        
        return description, data
    
    # Main dashboard content
    try:
        with st.spinner("Fetching GitLab data..."):
            main_group_id = get_group_id()
            all_group_ids = [main_group_id] + [sg["id"] for sg in get_subgroups(main_group_id)]
            
            projects = []
            for group_id in all_group_ids:
                projects.extend(get_group_projects(group_id))
            
            if not projects:
                st.warning("No projects found in the specified group path.")
                return
            
            # Summary stats
            st.subheader("📊 Activity Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Projects", len(projects))
            with col2:
                st.metric("Date Range", f"{start_date} to {end_date}")
            with col3:
                st.metric("Branch Flow", f"{merge_from} → {merge_to}")
            
            # Export button
            excel_data = generate_excel(projects, merge_from, merge_to, after.isoformat(), before.isoformat())
            st.download_button(
                label="📥 Export to Excel",
                data=excel_data,
                file_name=f"gitlab_activity_{start_date}_to_{end_date}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
            # Projects with activity
            st.subheader("🚀 Projects with Recent Activity")
            
            # Start a container div for all projects
            st.markdown("""
            <div class="projects-container">
            """, unsafe_allow_html=True)
            
            # Track if we have any projects with activity
            projects_with_activity = 0
            
            for project in projects:
                mrs = get_merged_mrs(project["id"], merge_from, merge_to, after.isoformat(), before.isoformat())
                tags = get_project_tags(project["id"], after.isoformat(), before.isoformat())
                
                if not mrs and not tags:
                    continue
                
                projects_with_activity += 1
                
                with st.container():
                    repo_name = extract_repo_name(project['path_with_namespace'])
                    st.markdown(f"""
                        <h3 style="margin-top: 0;"><span class="repo-name">{repo_name}</span></h3>
                    """, unsafe_allow_html=True)
                    
                    # MRs section
                    if mrs:
                        st.markdown(f"""
                        <h4 style="margin-bottom: 0.5rem;">Recent Merge Requests ({len(mrs)})</h4>
                        """, unsafe_allow_html=True)
                        
                        for mr in mrs[:1]:  # Only show 1 most recent MR
                            st.markdown(f"""
                            <div class="mr-item">
                                <a href="{mr['web_url']}" target="_blank" style="text-decoration: none; color: #2c3e50;">
                                    <strong>!{mr['iid']}</strong> - {mr['title']}
                                </a>
                                <div style="font-size: 0.85rem; color: #666;">
                                    Merged at {mr['merged_at']} by {mr['author']['name']}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Tags section
                    if tags:
                        tags_sorted = sorted(tags, key=lambda t: t["commit"]["committed_date"], reverse=True)
                        latest_tag = tags_sorted[0]
                        tag_name = latest_tag["name"]

                        tag_description, full_tag_obj = get_tag_info(project["id"], tag_name)
                        tag_date = latest_tag["commit"]["committed_date"]
                        
                        with st.expander(f"🔖 Latest Release: {tag_name}", expanded=False):
                            st.markdown(f"""
                            <div style="background-color: #e8f5e9; padding: 1rem; border-radius: 0.5rem;">
                                <h4 style="margin-top: 0;">{tag_name}</h4>
                                <p><strong>Released:</strong> {tag_date}</p>
                                <div style="background-color: white; padding: 1rem; border-radius: 0.25rem; margin-top: 0.5rem;">
                                    {tag_description}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    elif mrs:
                        st.markdown("""
                        <div class=""></div>
                        """, unsafe_allow_html=True)
                        st.warning("No tags released in this timeframe")
                    
                    st.markdown("</div>", unsafe_allow_html=True)  # Close project-card
                    st.markdown("""
                        <div class="section-divider"></div>
                        """, unsafe_allow_html=True)
                    
            # Close the projects container div
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Display a message if no projects have activity
            if projects_with_activity == 0:
                st.info("No projects with merge requests or tag activity were found in the selected date range.")
    
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from GitLab: {str(e)}")
    except Exception as e:
        logging.error("Unhandled exception: %s", traceback.format_exc())
        st.error("An unexpected error occurred. Please try again later.")

# Page routing
if not st.session_state.authenticated:
    login_page()
else:
    dashboard_page()