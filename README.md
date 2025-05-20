# GitLab Merge Request & Release Tracker

A Streamlit-based web application to track merge requests and releases across GitLab projects within a specified group. The app allows users to filter by date range, source and target branches, and group path, and export the activity data to an Excel file.

## Features
- **Authentication**: Secure login using a GitLab Personal Access Token.
- **Dashboard**: Displays recent merge requests and latest releases for projects in a specified GitLab group.
- **Filters**: Filter by date range, source branch, target branch, and group path.
- **Export**: Download project activity (repository name, merged from/to branches, tag name) as an Excel file.
- **Modern UI**: Responsive design with custom CSS for a professional look.
- **Caching**: Optimized API calls with Streamlit's caching for faster performance.

## Prerequisites
- **Python**: Version 3.7 or higher.
- **GitLab Personal Access Token**: With `api` scope for accessing GitLab data.
- **GitLab Instance**: Access to a GitLab instance (e.g., `https://gitlab.swifttech.com.np` or your own).

## Setup Instructions

### 1. Clone the Repository
Clone this repository to your local machine:
```bash
git clone <repository-url>
cd gitlab-mr-tracker
```

### 2. Set Up a Virtual Environment
Using a virtual environment is recommended to isolate dependencies.

#### On Windows
```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
venv\Scripts\activate
```

#### On macOS/Linux
```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```

After activation, you should see `(venv)` in your terminal prompt.

### 3. Install Required Packages
Install the necessary Python packages using pip:
```bash
pip install streamlit requests pandas xlsxwriter
```

#### Package Details
- **streamlit**: For building and running the web application.
- **requests**: For making HTTP requests to the GitLab API.
- **pandas**: For creating and manipulating DataFrames for Excel export.
- **xlsxwriter**: For generating formatted Excel files.

### 4. Run the Application
Start the Streamlit app:
```bash
streamlit run GitLab_MR_Tracker.py
```
This will launch the app in your default web browser at `http://localhost:8501`.

### 5. Configure the App
1. **Login**: Enter your GitLab Personal Access Token and the GitLab API base URL (default: `https://gitlab.swifttech.com.np/api/v4`).
2. **Filters**: In the sidebar, set the date range, source branch (e.g., `develop`), target branch (e.g., `testing1.1`), and group path (e.g., `bfi/backend`).
3. **Export**: Use the "Export to Excel" button to download activity data as an Excel file.

## Project Structure
```
gitlab-mr-tracker/
│
├── GitLab_MR_Tracker.py  # Main Streamlit app script
├── README.md             # Project documentation
└── venv/                 # Virtual environment (created after setup)
```

## Usage
1. **Login Page**:
   - Enter your GitLab Personal Access Token with `api` scope.
   - Specify the GitLab API base URL (e.g., `https://gitlab.swifttech.com.np/api/v4`).
   - Click "Login" to proceed to the dashboard.

2. **Dashboard**:
   - View a summary of total projects, date range, and branch flow.
   - Browse projects with recent merge requests or tags.
   - Expand release sections to view tag details.
   - Use the "Export to Excel" button to download a report containing:
     - Repository Name
     - Merged From Branch
     - Merged To Branch
     - Tag Name (or "none" if no tags)

3. **Filters**:
   - Adjust the date range to filter merge requests and tags.
   - Specify source and target branches for merge requests.
   - Set the group path to focus on specific GitLab groups.

4. **Logout**: Click the "Logout" button to clear the session and return to the login page.

## Troubleshooting
- **API Errors**: Ensure your GitLab token has the `api` scope and the base URL is correct.
- **No Projects Found**: Verify the group path (e.g., `bfi/backend`) exists and contains projects.
- **Excel Export Issues**: Ensure `pandas` and `xlsxwriter` are installed correctly.
- **Port Conflict**: If `http://localhost:8501` is in use, Streamlit will prompt for an alternative port.

## Notes
- The app caches API responses for 5 minutes (`ttl=300`) to improve performance.
- The Excel export includes only projects with merge requests or tags in the selected date range.
- The app is designed to work with any GitLab instance, not just `gitlab.swifttech.com.np`.

## License
This project is licensed under the MIT License.