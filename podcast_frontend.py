import streamlit as st
import pandas as pd

# Load the data
@st.cache_resource
def load_data():
    return pd.read_csv("pod_db_data.csv")

# Load the cached data
podcast_data = load_data()

# Title of the application
st.title("Podcast Episodes")

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
