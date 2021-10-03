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
from pathlib import Path
import userFunction as func
import warnings

warnings.filterwarnings('ignore')


######################################################################################
st.set_page_config(page_title="SMC Dashboard", page_icon=":desktop_computer:", layout="wide", initial_sidebar_state="auto")

# Initializae start date and end date to read the json files
startDate = datetime.datetime(2021, 8, 25)
# startDate = datetime.datetime(2021, 10, 2)
endDate = datetime.datetime(2021, 10, 3)

#user profile, followers, friends and timeline
user_Spotify = func.getuserProfile("Spotify", startDate, endDate)
followers_Spotify = func.getfollowersProfile("Spotify", startDate, endDate)
friends_Spotify = func.getfriendsProfile("Spotify", startDate, endDate)
timeline_Spotify = func.getuserTimeline("Spotify", endDate)
mutual_Spotify = func.getmutualFriends(friends_Spotify, followers_Spotify)
brandMention_Spotify = func.getbrand_Mention("Spotify", startDate,endDate)

user_AppleMusic = func.getuserProfile("AppleMusic", startDate, endDate)
followers_AppleMusic= func.getfollowersProfile("AppleMusic", startDate, endDate)
friends_AppleMusic = func.getfriendsProfile("AppleMusic", startDate, endDate)
timeline_AppleMusic = func.getuserTimeline("AppleMusic", endDate)
mutual_AppleMusic = func.getmutualFriends(friends_AppleMusic, followers_AppleMusic)
brandMention_AppleMusic = func.getbrand_Mention("AppleMusic", startDate,endDate)

user_YoutubeMusic = func.getuserProfile("youtubemusic", startDate, endDate)
followers_YoutubeMusic= func.getfollowersProfile("youtubemusic", startDate, endDate)
friends_YoutubeMusic = func.getfriendsProfile("youtubemusic", startDate, endDate)
timeline_YoutubeMusic = func.getuserTimeline("youtubemusic", endDate)
mutual_YoutubeMusic = func.getmutualFriends(friends_YoutubeMusic, followers_YoutubeMusic)
brandMention_YoutubeMusic = func.getbrand_Mention("youtubemusic", startDate,endDate)

#profile image
img_Spotify = func.getprofileImg("Spotify", endDate)
img_AppleMusic = func.getprofileImg("AppleMusic", endDate)
img_YoutubeMusic = func.getprofileImg("youtubemusic", endDate)

accName = st.sidebar.selectbox(
    "Select Social Media Account:",
    ['Spotify', 'AppleMusic', 'YoutubeMusic'],
    help="Choose Social Media account"
)

st.sidebar.markdown("***")
st.sidebar.write("Options for Demographic Visualization")

freq = st.sidebar.selectbox(
    "Choose the desired frequency",
    ('Yearly', 'Quarterly', 'Monthly'),
    help="Frequency for user demographic visualization"
)

df_profileOption = st.sidebar.selectbox(
    "Choose to visualize followers or friends demographic",
    ('followers', 'friends'),
    help="Choose to view account creation date for followers or friends"
)

st.sidebar.markdown("***")
st.sidebar.write("Options for Growth Rate Visualization")
avg_rate = st.sidebar.selectbox(
    "Choose the attribute for the growth rate",
    ('followers_count', 'friends_count', 'num_of_tweet', 'favourite_count'),
    help="Choose to view which attribute for growth rate"
)

startDate_select = st.sidebar.date_input("Start Date:", value=endDate - datetime.timedelta(days=14),
                                         min_value=datetime.date(2021, 8, 25), max_value=datetime.date.today(),
                                         help="Select the start date for visualization")
endDate_select = st.sidebar.date_input("End Date:", value= endDate,
                                       min_value=datetime.date(2021, 8, 25),
                                       max_value=datetime.date.today(), help="Select the end date for visualization")
if startDate_select > endDate_select:
    st.error("Selected start date is larger than the selected end date")

st.title("Social Media Computing Assignment 1")

# Assign selected account as target and others as competitor
if accName == "Spotify":
    img_target = img_Spotify
    df_target = user_Spotify
    df_competitor1 = user_AppleMusic
    df_competitor2 = user_YoutubeMusic

    df_mutual = mutual_Spotify
    df_brandMention = brandMention_Spotify

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

    df_mutual = mutual_AppleMusic
    df_brandMention = brandMention_AppleMusic

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

    df_mutual = mutual_YoutubeMusic
    df_brandMention = brandMention_YoutubeMusic

    followers_target = followers_YoutubeMusic
    followers_competitor1 = followers_AppleMusic
    followers_competitor2 = followers_Spotify

    friends_target = friends_YoutubeMusic
    friends_competitor1 = friends_AppleMusic
    friends_competitor2 = friends_Spotify

    timeline_target = timeline_YoutubeMusic
    timeline_competitor1 = timeline_AppleMusic
    timeline_competitor2 = timeline_Spotify

acc_img, acc_title = st.columns([1, 10])
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
                    <p class="logo-text"> {accName} Dashboard</p>
                </div>
                """,
        unsafe_allow_html=True
        )

func.emptyLine()

st.subheader(f"{accName}'s Metrics")
col_metrics1, col_metrics2, col_metrics3 = st.columns(3)
# get the KPI
date_today, date_yesterday = func.getDate(endDate)
followers_num, followers_diff, friends_num, friends_diff, tweet_num, tweet_diff, fav_num, fav_diff = func.getKPI(df_target,
                                                                                                            date_today,
                                                                                                            date_yesterday)


with col_metrics1:
    st.metric("Number of Followers:", followers_num, followers_diff)
    st.metric("Number of Friends:", friends_num, friends_diff)
with col_metrics2:
    st.metric("Number of Tweet:", tweet_num, tweet_diff)
    st.metric("Number of Favourite:", fav_num, fav_diff)
with col_metrics3:
    st.metric("Number of mutual Friends:", len(df_mutual))
    st.write("")
    # st.metric("Empty Metrics", 0)

func.emptyLine()

col_topMention, col_topHashtag,col_topDoCFollowers, col_topDoCFriends = st.columns(4)
with col_topMention:
    topMention_num = st.slider("Display how many top mention users?", min_value=0, max_value=10, value=3)
    st.subheader(f"{accName}'s Top Mentions")
    topMention_df = func.get_topMention(timeline_target)
    topMention_df = topMention_df.loc[:topMention_num - 1, :]
    topMention_df
with col_topHashtag:
    topHashtag_num = st.slider("Display how many top hashtags?", min_value=0, max_value=10, value=3)
    st.subheader(f"{accName}'s Top Hashtags")
    topHashtag_df = func.get_topHashtag(timeline_target)
    topHashtag_df = topHashtag_df.loc[:topHashtag_num - 1, :]
    topHashtag_df

# col_topDoCFollowers, col_topDoCFriends = st.columns(2)
with col_topDoCFollowers:
    topFollowerDoC_num = st.slider("Display how many users?", min_value=0, max_value=10, value=3, key='DoC_Followers')
    st.subheader(f"{accName}'s Top Degree of Centrality for Followers")
    topDoC_Followers = func.get_topFollowerDoC(followers_target)
    topDoC_Followers = topDoC_Followers.loc[:topFollowerDoC_num - 1, :]
    topDoC_Followers
with col_topDoCFriends:
    topFriendDoC_num = st.slider("Display how many users?", min_value=0, max_value=10, value=3, key='DoC_Friends')
    st.subheader(f"{accName}'s Top Degree of Centrality for Friends")
    topDoC_Friends = func.get_topFriendDoC(friends_target)
    topDoC_Friends = topDoC_Friends.loc[:topFriendDoC_num - 1, :]
    topDoC_Friends

func.emptyLine()

col_engagementTweetType, col_engagementTimeType, col_engagementBrandMention = st.columns(3)
#average engagement based on types of tweet
with col_engagementTweetType:
    st.subheader(f"{accName}'s Average Engagement Based on Tweet Type")
    expander_engagementTweetType = st.expander(label='Set Conditions')
    with expander_engagementTweetType:
        days_select_E1 = st.number_input("Enter number of days:", min_value=0, value=7, step=1, key="num_tweetType_days")
        engagement_tweetType_df = func.engagement_tweetType(timeline_target, days_select_E1)
        TWEET_TYPE = engagement_tweetType_df['Tweet_Type'].unique()
        TWEET_TYPE_SELECTED = st.multiselect("Select the Tweet Type",TWEET_TYPE, default=TWEET_TYPE)
        ENGAGEMENT_TYPE_1 = engagement_tweetType_df['Engagement'].unique()
        ENGAGEMENT_SELECTED_1 = st.multiselect("Select the Engagements", ENGAGEMENT_TYPE_1, default=ENGAGEMENT_TYPE_1, key="select_tweetType_engagement")
    days_select_E1 = int(days_select_E1)
    st.write(f"The average engagement for the last {days_select_E1} days")
    mask_tweetType = engagement_tweetType_df['Tweet_Type'].isin(TWEET_TYPE_SELECTED)
    engagement_tweetType_df = engagement_tweetType_df[mask_tweetType]
    mask_Engagement = engagement_tweetType_df['Engagement'].isin(ENGAGEMENT_SELECTED_1)
    engagement_tweetType_df = engagement_tweetType_df[mask_Engagement]
    st.dataframe(engagement_tweetType_df)

#average engagement based on time of the day
with col_engagementTimeType:
    st.subheader(f"{accName}'s Average Engagement Based on Time Posted")
    expander_engagementTimeType = st.expander(label='Set Conditions')
    with expander_engagementTimeType:
        days_select_E2 = st.number_input("Enter number of days:", min_value=0, value=7, step=1, key="num_time_days")
        engagement_time_df = func.engagement_timeBin(timeline_target, days_select_E2)
        TIME_BIN = engagement_time_df['Time_Bin'].unique()
        TIME_BIN_SELECTED = st.multiselect("Select the Time Bin", options=TIME_BIN, default=TIME_BIN)
        ENGAGEMENT_TYPE_2 = engagement_time_df['Engagement'].unique()
        ENGAGEMENT_SELECTED_2 = st.multiselect("Select the Engagements", ENGAGEMENT_TYPE_2, default=ENGAGEMENT_TYPE_2, key="select_time_engagement")
    days_select_E2 = int(days_select_E2)
    st.write(f"The average engagement for the last {days_select_E2} days")
    mask_timeBin = engagement_time_df['Time_Bin'].isin(TIME_BIN_SELECTED)
    engagement_time_df = engagement_time_df[mask_tweetType]
    mask_Engagement = engagement_time_df['Engagement'].isin(ENGAGEMENT_SELECTED_2)
    engagement_time_df = engagement_time_df[mask_Engagement]
    st.dataframe(engagement_time_df)

#average engagement based on popular brand mention
with col_engagementBrandMention:
    st.subheader(f"{accName}'s Average Engagement Based on Popular Brand Mention")
    expander_engagementBrandMention = st.expander(label='Set Conditions')
    with expander_engagementBrandMention:
        days_select_E3 = st.number_input("Enter number of days:", min_value=0, value=7, step=1, key="num_brand_days")
    days_select_E3 = int(days_select_E3)
    st.write(f"The average engagement for the last {days_select_E3} days")
    engagementBrandMention = func.engagement_BrandMention(df_brandMention, days_select_E3)
    engagementBrandMention

func.emptyLine()

col_profileDemographic, col_growthRate = st.columns(2)
with col_profileDemographic:
    st.subheader(f"{accName}'s User Demographic {freq}")
    if freq == "Yearly":
        freq = "Y"
    elif freq == "Quarterly":
        freq = "Q"
    elif freq == "Monthly":
        freq = "M"
    func.profileDemographic(accName, followers_target, friends_target, df_profileOption, freq)
with col_growthRate:
    # Visualize average growth rate
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