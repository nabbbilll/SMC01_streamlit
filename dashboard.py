import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
import pytz
import json
import datetime
import time
import math
import userFunction as func
import warnings
warnings.filterwarnings('ignore')


######################################################################################
accName = st.sidebar.selectbox(
    "Select Social Media Account:",
    ['Spotify', 'AppleMusic', 'YoutubeMusic']
)

startDate_select = st.sidebar.date_input("Start Date:", value=datetime.date(2021, 8, 25),
                                         min_value=datetime.date(2021, 8, 25), max_value=datetime.date.today(),
                                         help="Select the start date")
endDate_select = st.sidebar.date_input("End Date:", min_value=datetime.date(2021, 8, 25),
                                       max_value=datetime.date.today(), help="Select the end date")

if startDate_select > endDate_select:
    st.error("Selected start date is larger than the selected end date")

freq = st.sidebar.selectbox(
    "Choose the desired frequency",
    ('Yearly','Quarterly','Monthly')
)

avg_rate = st.sidebar.selectbox(
    "Choose the attribute for the growth rate",
    ('followers_count', 'friends_count','num_of_tweet', 'favourite_count')
)

st.title("Social Media Computing Assignment 1")

st.header(f"{accName} Dashboard KPI")
# st.write(f"Selected Start Date: {startDate}")
# st.write(f"Selected End Date: {endDate}")

# st.write(f"{accName} DataFrame:")

# Initializae start date and end date to read the json files
startDate = datetime.datetime(2021, 8, 25)
endDate = datetime.datetime(2021, 9, 12)

user_Spotify = func.getuserProfile("Spotify", startDate, endDate)
followers_Spotify = func.getfollowersProfile("Spotify", endDate)
friends_Spotify = func.getfriendsProfile("Spotify", endDate)
user_AppleMusic = func.getuserProfile("AppleMusic", startDate, endDate)
followers_AppleMusic= func.getfollowersProfile("AppleMusic", endDate)
friends_AppleMusic = func.getfriendsProfile("AppleMusic", endDate)
user_YoutubeMusic = func.getuserProfile("youtubemusic", startDate, endDate)
followers_YoutubeMusic= func.getfollowersProfile("youtubemusic", endDate)
friends_YoutubeMusic = func.getfriendsProfile("youtubemusic", endDate)

# Assign selected account as target and others as competitor
if accName == "Spotify":
    df_target = user_Spotify
    df_competitor1 = user_AppleMusic
    df_competitor2 = user_YoutubeMusic

    followers_target = followers_Spotify
    followers_competitor1 = followers_AppleMusic
    followers_competitor2 = followers_YoutubeMusic

    friends_target = friends_Spotify
    friends_competitor1 = friends_AppleMusic
    friends_competitor2 = friends_YoutubeMusic
elif accName == "AppleMusic":
    df_target = user_AppleMusic
    df_competitor1 = user_Spotify
    df_competitor2 = user_YoutubeMusic

    followers_target = followers_AppleMusic
    followers_competitor1 = followers_Spotify
    followers_competitor2 = followers_YoutubeMusic

    friends_target = friends_AppleMusic
    friends_competitor1 = friends_Spotify
    friends_competitor2 = friends_YoutubeMusic
elif accName == "YoutubeMusic":
    df_target = user_YoutubeMusic
    df_competitor1 = user_AppleMusic
    df_competitor2 = user_Spotify

    followers_target = followers_YoutubeMusic
    followers_competitor1 = followers_AppleMusic
    followers_competitor2 = followers_Spotify

    friends_target = friends_YoutubeMusic
    friends_competitor1 = friends_AppleMusic
    friends_competitor2 = friends_Spotify

#df_target
col_1, col_2 = st.columns(2)
# get the KPI
date_today, date_yesterday = func.getDate(endDate)
# print(date_today)
# print(date_yesterday)
followers_num, followers_diff, friends_num, friends_diff, tweet_num, tweet_diff, fav_num, fav_diff = func.getKPI(df_target,
                                                                                                            date_today,
                                                                                                            date_yesterday)

with col_1:
    st.metric("Today Number of Followers:", followers_num, followers_diff)
    st.metric("Today Number of Friends:", friends_num, friends_diff)
with col_2:
    st.metric("Today Number of Tweet:", tweet_num, tweet_diff)
    st.metric("Today Number of Favourite:", fav_num, fav_diff)

func.emptyLine()

col_3, col_4 = st.columns(2)
with col_3:
    st.markdown(f"{accName}'s User Demographic {freq}:")
    #freq = st.selectbox("Choose the desired frequency",('Yearly','Quarterly','Monthly'))
    if freq == "Yearly":
        freq = "Y"
    elif freq == "Quarterly":
        freq = "Q"
    elif freq == "Monthly":
        freq = "M"
    func.followers_demographic(accName, followers_target, freq)
with col_4:
    if avg_rate == "followers_count":
        avg_name = "followers count"
    elif avg_rate == "friends_count":
        avg_name = "friends count"
    elif avg_rate == "num_of_tweet":
        avg_name = "tweet count"
    elif avg_rate == "favourite_count":
        avg_name = "favourite count"
    st.markdown(f"{accName}'s Average Growth Rate for {avg_name} :")
    func.growthRate(accName, df_target, avg_rate, startDate_select, endDate_select)

func.emptyLine()