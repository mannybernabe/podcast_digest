import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from gsheetsdb import connect

# Setting up a connection to Google Sheets
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)
conn = connect(credentials=credentials)

# Fetch the data from Google Sheets
@st.cache_resource
def load_data():
    sheet_url = st.secrets["private_gsheets_url"]
    query = f'SELECT * FROM "{sheet_url}"'
    rows = conn.execute(query, headers=1)
    df = pd.DataFrame(rows.fetchall())
    return df

# Load the cached data
podcast_data = load_data()

# Title of the application
st.title("Podcast Episodes_2")

# Function to truncate the summary for a preview
def truncate_summary(summary, max_length=100):
    if len(summary) > max_length:
        return summary[:max_length] + "..."
    else:
        return summary

# Display each podcast episode with the new layout
for index, row in podcast_data.iterrows():
    # Use columns to create a side-by-side layout
    col1, col2 = st.columns([1, 3])  # Adjust the numbers for desired width ratio

    # Display thumbnail in the left column (col1)
    col1.image(row['pod_thumbnail'], use_column_width=True)
    
    # Display podcast details in the right column (col2)
    col2.subheader(row['eps_title'])
    col2.write(f"**Podcast:** {row['pod_title']}")
    
    # Display duration and date on the same line
    duration_col, date_col = col2.columns(2)
    duration_col.write(f"**Duration:** {row['eps_length']}")
    date_col.write(f"{row['pulished_date']}")
    
    # Show a truncated preview of the summary in the right column
    preview = truncate_summary(row['summary'])
    col2.write(preview)
    
    # "Read more" effect using markdown
    read_more = col2.button("Read more", key=f"btn_{index}")
    if read_more:
        col2.write(row['summary'])
    
    st.write("---")
