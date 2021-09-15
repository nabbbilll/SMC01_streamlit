import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
import pytz
import json
import datetime
import time
import math
from collections import Counter
import userFunction as func
import warnings
import base64
warnings.filterwarnings('ignore')


######################################################################################
# Initializae start date and end date to read the json files
startDate = datetime.datetime(2021, 8, 25)
endDate = datetime.datetime(2021, 9, 15)
#user profile, followers, friends and timeline
user_Spotify = func.getuserProfile("Spotify", startDate, endDate)
followers_Spotify = func.getfollowersProfile("Spotify", endDate)
friends_Spotify = func.getfriendsProfile("Spotify", endDate)
timeline_Spotify = func.getuserTimeline("Spotify", endDate)
user_AppleMusic = func.getuserProfile("AppleMusic", startDate, endDate)
followers_AppleMusic= func.getfollowersProfile("AppleMusic", endDate)
friends_AppleMusic = func.getfriendsProfile("AppleMusic", endDate)
timeline_AppleMusic = func.getuserTimeline("AppleMusic", endDate)
user_YoutubeMusic = func.getuserProfile("youtubemusic", startDate, endDate)
followers_YoutubeMusic= func.getfollowersProfile("youtubemusic", endDate)
friends_YoutubeMusic = func.getfriendsProfile("youtubemusic", endDate)
timeline_YoutubeMusic = func.getuserTimeline("youtubemusic", endDate)
#profile image
img_Spotify = func.getprofileImg("Spotify", endDate)
img_AppleMusic = func.getprofileImg("AppleMusic", endDate)
img_YoutubeMusic = func.getprofileImg("youtubemusic", endDate)

accName = st.sidebar.selectbox(
    "Select Social Media Account:",
    ['Spotify', 'AppleMusic', 'YoutubeMusic'],
    help="Choose Social Media account"
)

startDate_select = st.sidebar.date_input("Start Date:", value=datetime.date(2021, 8, 25),
                                         min_value=datetime.date(2021, 8, 25), max_value=datetime.date.today(),
                                         help="Select the start date for visualization")
endDate_select = st.sidebar.date_input("End Date:", min_value=datetime.date(2021, 8, 25),
                                       max_value=datetime.date.today(), help="Select the end date for visualization")

if startDate_select > endDate_select:
    st.error("Selected start date is larger than the selected end date")

freq = st.sidebar.selectbox(
    "Choose the desired frequency",
    ('Yearly','Quarterly','Monthly'),
    help="Frequency for user demographic visualization"
)

avg_rate = st.sidebar.selectbox(
    "Choose the attribute for the growth rate",
    ('followers_count', 'friends_count','num_of_tweet', 'favourite_count')
)

st.title("Social Media Computing Assignment 1")

# st.write(f"Selected Start Date: {startDate}")
# st.write(f"Selected End Date: {endDate}")

# st.write(f"{accName} DataFrame:")

# Assign selected account as target and others as competitor
if accName == "Spotify":
    img_target = img_Spotify
    df_target = user_Spotify
    df_competitor1 = user_AppleMusic
    df_competitor2 = user_YoutubeMusic

    followers_target = followers_Spotify
    followers_competitor1 = followers_AppleMusic
    followers_competitor2 = followers_YoutubeMusic

    friends_target = friends_Spotify
    friends_competitor1 = friends_AppleMusic
    friends_competitor2 = friends_YoutubeMusic

    timeline_target = timeline_Spotify
    timeline_competitor1 = timeline_AppleMusic
    timeline_competitor2 = timeline_YoutubeMusic
elif accName == "AppleMusic":
    img_target = img_AppleMusic
    df_target = user_AppleMusic
    df_competitor1 = user_Spotify
    df_competitor2 = user_YoutubeMusic

    followers_target = followers_AppleMusic
    followers_competitor1 = followers_Spotify
    followers_competitor2 = followers_YoutubeMusic

    friends_target = friends_AppleMusic
    friends_competitor1 = friends_Spotify
    friends_competitor2 = friends_YoutubeMusic

    timeline_target = timeline_AppleMusic
    timeline_competitor1 = timeline_Spotify
    timeline_competitor2 = timeline_YoutubeMusic
elif accName == "YoutubeMusic":
    img_target = img_YoutubeMusic
    df_target = user_YoutubeMusic
    df_competitor1 = user_AppleMusic
    df_competitor2 = user_Spotify

    followers_target = followers_YoutubeMusic
    followers_competitor1 = followers_AppleMusic
    followers_competitor2 = followers_Spotify

    friends_target = friends_YoutubeMusic
    friends_competitor1 = friends_AppleMusic
    friends_competitor2 = friends_Spotify

    timeline_target = timeline_YoutubeMusic
    timeline_competitor1 = timeline_AppleMusic
    timeline_competitor2 = timeline_Spotify

title_container = st.container()
acc_img, acc_title = st.columns([1, 10])
with title_container:
    with acc_img:
        st.markdown(
            """
            <style>
            .container {
                display: flex;
            }
            .logo-img {
                float:right;
                width: 80px;
                height:80px;
            }
            .logo-text {
                font-weight:50px;
                font-size:40px;
                padding-top: 25px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            f"""
            <div class="container">
                <img class="logo-img" src="{img_target}">
            </div>
            """,
            unsafe_allow_html=True
        )
    with acc_title:
        st.markdown(
            f"""
                    <div class="container">
                        <p class="logo-text"> {accName} Dashboard KPI</p>
                    </div>
                    """,
            unsafe_allow_html=True
        )
func.emptyLine()

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
    st.metric("Number of Followers:", followers_num, followers_diff)
    st.metric("Number of Friends:", friends_num, friends_diff)
with col_2:
    st.metric("Number of Tweet:", tweet_num, tweet_diff)
    st.metric("Number of Favourite:", fav_num, fav_diff)

func.emptyLine()

col_topMention, col = st.columns(2)
with col_topMention:
    #display more beautiful or change to table
    st.subheader(f"{accName}'s Top Mentions")
    func.get_topMention(timeline_target)
with col:
    st.write("empty")

func.emptyLine()

col_demographic, col_growthRate = st.columns(2)
with col_demographic:
    st.subheader(f"{accName}'s User Demographic {freq}")
    #freq = st.selectbox("Choose the desired frequency",('Yearly','Quarterly','Monthly'))
    if freq == "Yearly":
        freq = "Y"
    elif freq == "Quarterly":
        freq = "Q"
    elif freq == "Monthly":
        freq = "M"
    func.followers_demographic(accName, followers_target, freq)
with col_growthRate:
    if avg_rate == "followers_count":
        avg_name = "followers count"
    elif avg_rate == "friends_count":
        avg_name = "friends count"
    elif avg_rate == "num_of_tweet":
        avg_name = "tweet count"
    elif avg_rate == "favourite_count":
        avg_name = "favourite count"
    st.subheader(f"{accName}'s Average Growth Rate for {avg_name}")
    func.growthRate(accName, df_target, avg_rate, startDate_select, endDate_select)

func.emptyLine()