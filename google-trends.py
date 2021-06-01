import streamlit as st

from pytrends.request import TrendReq
pytrends = TrendReq(hl='en-US', tz=360)

import pandas as pd

from datetime import datetime, date, time

import numpy as np
import base64

# Cleans up the keywords and deals with special chars, white space, etc:

def removeRestrictedCharactersAndWhiteSpaces(keywords):

    restricted_characters = ['-', ',', '\'', ')', '(', '[', ']', '{', '}', '.', '*', '?', '_', '@', '!', '$']

    preprocessed_list = []
    
    for keyword in keywords:
    
        clean_keyword = ""
        for char in keyword:
            if char not in restricted_characters:
                clean_keyword += char
        
        white_space_counter = 0
        
        for char in clean_keyword:
            if char == ' ':
                white_space_counter += 1
            else:
                break
        
        clean_keyword = clean_keyword[white_space_counter:]
        
        white_space_counter = 0
        
        for i in range(len(clean_keyword) - 1, 0, -1):
            if clean_keyword[i] == ' ':
                white_space_counter += 1
            else:
                break
        
        if white_space_counter != 0:
            clean_keyword = clean_keyword[:-white_space_counter]
        
        preprocessed_list.append(clean_keyword)
    
    return preprocessed_list

st.set_page_config(layout="wide")

st.image('https://landerapp.com/blog/wp-content/uploads/2018/04/google-trends.jpg', width=300)
st.title("Google Trends Analyzer")
st.markdown('**Top & Rising Google Trends Dashboard (USA)**') 

# Here's where we ask the user to provide their search terms

linesDeduped2 = []

MAX_LINES = 5

text2 = st.markdown("Get Top & Rising trends for up to 5 search terms, directly from Google Trends. Enter one search term per line, select your time period & hit 'Get Trends'")
text = st.text_area("Special thanks to Orit Mutznik (@oritsimu) for providing the inspiration. Remember, kids - good artists copy and great artists steal!", height=150, key=1)
lines = text.split("\n")  # A list of lines
linesList = []
for x in lines:
    linesList.append(x)
linesList = list(dict.fromkeys(linesList))  # Remove dupes
linesList = list(filter(None, linesList))  # Remove empty

# This logic handles someone who enters >5 search terms

if len(linesList) > MAX_LINES:
    st.warning(f"⚠️ Only the first 5 search terms will be analyzed! Gordon Gekko was wrong about greed being good!!")
    linesList = linesList[:MAX_LINES]
        
# Date range selection
        
selected_timeframe = ""

period_list = ["Past 12 months", "Past hour", "Past 4 hours", "Past day", "Past 7 days", "Past 30 days", "Past 90 days", "Past 5 years", "2004 - present", "Custom time range"]
tf = ["today 12-m", "now 1-H", "now 4-H", "now 1-d", "now 7-d", "today 1-m", "today 3-m", "today 5-y", "all", "custom"]
timeframe_selectbox = st.selectbox("Choose Time Period", period_list)

idx = period_list.index(timeframe_selectbox)

selected_timeframe = tf[idx]

todays_date = date.today()

current_year = todays_date.year

years = list(range(2005, current_year + 1))
months = list(range(1, 13))
days = list(range(1, 32))

if selected_timeframe == "custom":
    
    st.write(f"From")

    col11, col12, col13 = st.beta_columns(3)
    year_from = col11.selectbox("year", years, key="0")
    month_from = col12.selectbox("month", months, key="1")
    day_from = col13.selectbox("day", days, key="2")
    
    st.write(f"To")

    col21, col22, col23 = st.beta_columns(3)
    year_to = col21.selectbox("year", years, key="3")
    month_to = col22.selectbox("month", months, key="4")
    day_to = col23.selectbox("day", days, key="5")
    
    selected_timeframe = str(year_from) + "-" + str(month_from) + "-" + str(day_from) + " " + str(year_to) + "-" + str(month_to) + "-" + str(day_to)
        
start_execution = st.button("🚀 Get Trends!")

# This returns the insights for the search terms. If none are provided, there's an error message

if start_execution:

    if len(linesList) == 0:
    
        st.warning("🚩 Would you be so kind as to enter at least 1 search term?")
        
    else:
    
        linesList = removeRestrictedCharactersAndWhiteSpaces(linesList)
        
        pytrends.build_payload(linesList, timeframe=selected_timeframe, cat=0, geo='US', gprop='')
        related_queries = pytrends.related_queries()
        
        for i in range(len(linesList)):

            st.header("Google Trends data for keyword {}: {}".format(i+1, str(linesList[i])))
            
            c29, c30, c31 = st.beta_columns([6, 2, 6])
            
            with c29:

                st.subheader("🔝 Top Trends")
                st.write(related_queries.get(linesList[i]).get("top"))
                        
            with c31:

                st.subheader("⏫ Rising Trends")
                st.write(related_queries.get(linesList[i]).get("rising"))               
        
        st.write("""## 📈 Search Interest Over Time""")
        pytrends.interest_over_time()
        df = pytrends.interest_over_time()
        df.drop("isPartial", axis = "columns", inplace = True)
        st.line_chart(data=df, width=0, height=0, use_container_width=True)
        
        st.write("""## 🔥 Top 10 (general) searches trending in the USA right now""")
        dt = pytrends.trending_searches(pn = 'united_states').head(10)
        st.write(dt)                    
        
        st.stop()