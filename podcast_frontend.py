import streamlit as st
import pandas as pd
import requests
from google.oauth2 import service_account
from gsheetsdb import connect
from datetime import datetime

# Function to send RSS URL to the pipeline
def send_to_pipeline(url):
    endpoint = "https://eoa39xndc36ekvy.m.pipedream.net/"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'pipedream/1'
    }
    data = {
        "rss_URL_input": url
    }
    response = requests.post(endpoint, headers=headers, json=data)
    return response

# Setting up a connection to Google Sheets
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)
conn = connect(credentials=credentials)

# Uses st.cache_data to only rerun when the query changes or after 2 minutes.
@st.cache_data(ttl=120)
def load_data():
    sheet_url = st.secrets["private_gsheets_url"]
    query = f'SELECT * FROM "{sheet_url}"'
    rows = conn.execute(query, headers=1)
    df = pd.DataFrame(rows.fetchall())
    df = df.sort_values(by="pulished_date", ascending=False)
    return df

# Load the cached data
podcast_data = load_data()

# RSS Feed Handling in the Sidebar
st.sidebar.header("RSS Feed Input")
rss_url = st.sidebar.text_input("Enter RSS Feed URL:")
submit_rss = st.sidebar.button("Submit")

if submit_rss:
    if rss_url:
        try:
            response = send_to_pipeline(rss_url)
            if response.status_code == 200:
                st.sidebar.success("RSS feed URL submitted for processing!")
                st.sidebar.info("Please wait a few minutes and update the app.")
            else:
                st.sidebar.error(f"Error submitting the RSS feed URL. Status code: {response.status_code}")
        except Exception as e:
            st.sidebar.error(f"Error submitting the RSS feed URL: {e}")
    else:
        st.sidebar.warning("Please provide a valid RSS feed URL.")

# Title of the application
st.title("Business Wisdom at Your Fingertips: The Ultimate Podcast Roundup!")

# Function to truncate the summary for a preview
def truncate_summary(summary, max_length=100):
    if len(summary) > max_length:
        return summary[:max_length] + "..."
    else:
        return summary

# Display each podcast episode with the new layout
for index, row in podcast_data.iterrows():
    col1, col2 = st.columns([1, 3])

    col1.image(row['pod_thumbnail'], use_column_width=True)
    
    col2.subheader(row['eps_title'])
    col2.write(f"**Podcast:** {row['pod_title']}")
    
    formatted_date = datetime.strptime(row['pulished_date'], '%a, %d %b %Y %H:%M:%S %z').strftime('%a, %d %b')
    duration_col, date_col = col2.columns(2)
    duration_col.write(f"**Duration:** {row['eps_length']}")
    date_col.write(formatted_date)
    
    preview = truncate_summary(row['summary'])
    col2.write(preview)
    
    read_more = col2.button("Read more", key=f"btn_{index}")
    if read_more:
        col2.write(row['summary'])
    
    st.write("---")
