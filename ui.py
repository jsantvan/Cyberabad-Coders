import streamlit as st
import json
import pandas as pd
from dateutil import parser

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="NewsStream UI", page_icon="📰")

# --- Auto-Refresh Component ---
# This line adds a meta refresh tag to the page's HTML, telling the browser
# to reload every 600 seconds (10 minutes).
st.html("<meta http-equiv='refresh' content='60'>")

# --- Main App ---
st.title("📰 NewsStream Dashboard")
OUTPUT_FILE = "data/processed_articles.jsonl"


@st.cache_data
def load_data():
    """Loads and processes data, returns a pandas DataFrame."""
    records = []
    try:
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                record = json.loads(line)
                if record.get("status") == "success":
                    flat_record = {
                        "title": record["data"]["original_title"],
                        "link": record["data"]["link"],
                        "published_str": record["data"]["published"],
                        "summary": record["data"]["processed_content"]["summary"],
                        "category": record["data"]["processed_content"]["category"],
                        "sentiment": record["data"]["processed_content"]["sentiment"],
                    }
                    try:
                        flat_record["published_date"] = parser.parse(flat_record["published_str"]).date()
                    except (ValueError, TypeError):
                        flat_record["published_date"] = None
                    records.append(flat_record)
    except FileNotFoundError:
        return pd.DataFrame()

    return pd.DataFrame(records)


df = load_data()

if df.empty:
    st.warning("No data found. Run main.py to fetch articles.", icon="⚠️")
else:
    # --- Sidebar Filters ---
    st.sidebar.header("Filter Articles")
    categories = sorted(df['category'].unique())
    selected_categories = st.sidebar.multiselect("Category", options=categories, default=categories)
    sentiments = sorted(df['sentiment'].unique())
    selected_sentiments = st.sidebar.multiselect("Sentiment", options=sentiments, default=sentiments)
    min_date = df['published_date'].min()
    max_date = df['published_date'].max()
    selected_date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    start_date, end_date = selected_date_range
    filtered_df = df[
        (df['category'].isin(selected_categories)) &
        (df['sentiment'].isin(selected_sentiments)) &
        (df['published_date'] >= start_date) &
        (df['published_date'] <= end_date)
        ]

    st.success(f"Showing {len(filtered_df)} of {len(df)} total articles")

    for index, row in filtered_df.sort_values(by="published_date", ascending=False).iterrows():
        st.divider()
        st.subheader(row['title'])

        col1, col2, col3 = st.columns(3)
        col1.markdown(f"**🗓️ Date:** {row['published_date'].strftime('%d %b %Y')}")
        col2.markdown(f"**🏷️ Category:** `{row['category']}`")
        col3.markdown(f"**😃 Sentiment:** `{row['sentiment']}`")

        with st.expander("Read Summary"):
            st.write(row['summary'])

        st.link_button("Read Full Article", row['link'])