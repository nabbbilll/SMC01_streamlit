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
import csv
import matplotlib.pyplot as plt

import nltk
from nltk.tokenize import TweetTokenizer
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import re
import emoji
import string
from wordcloud import WordCloud
from textblob import TextBlob

import networkx as nx
from operator import itemgetter
import community
import streamlit.components.v1 as components
from pyvis.network import Network

warnings.filterwarnings('ignore')

######################################################################################
st.set_page_config(page_title="SMC Dashboard", page_icon=":desktop_computer:", layout="wide", initial_sidebar_state="auto")
st.set_option('deprecation.showPyplotGlobalUse', False)

# Initialize start date and end date to read the json files
startDate = datetime.datetime(2021, 8, 25)
endDate = datetime.datetime(2021, 11, 2)

# user profile, followers, friends and timeline
user_Spotify = func.getuserProfile("Spotify")
followers_Spotify = func.getfollowersProfile("Spotify")
friends_Spotify = func.getfriendsProfile("Spotify")
timeline_Spotify = func.getuserTimeline("Spotify")
mutual_Spotify = func.getmutualFriends(friends_Spotify, followers_Spotify)
brandMention_Spotify = func.getbrand_Mention("Spotify")
network_Spotify = func.getNetworkStats("Spotify")

user_AppleMusic = func.getuserProfile("AppleMusic")
followers_AppleMusic= func.getfollowersProfile("AppleMusic")
friends_AppleMusic = func.getfriendsProfile("AppleMusic")
timeline_AppleMusic = func.getuserTimeline("AppleMusic")
mutual_AppleMusic = func.getmutualFriends(friends_AppleMusic, followers_AppleMusic)
brandMention_AppleMusic = func.getbrand_Mention("AppleMusic")
network_AppleMusic = func.getNetworkStats("AppleMusic")


user_YoutubeMusic = func.getuserProfile("youtubemusic")
followers_YoutubeMusic= func.getfollowersProfile("youtubemusic")
friends_YoutubeMusic = func.getfriendsProfile("youtubemusic")
timeline_YoutubeMusic = func.getuserTimeline("youtubemusic")
mutual_YoutubeMusic = func.getmutualFriends(friends_YoutubeMusic, followers_YoutubeMusic)
brandMention_YoutubeMusic = func.getbrand_Mention("youtubemusic")
network_YoutubeMusic = func.getNetworkStats("youtubemusic")


# get profile image
img_Spotify = func.getprofileImg(user_Spotify)
img_AppleMusic = func.getprofileImg(user_AppleMusic)
img_YoutubeMusic = func.getprofileImg(user_YoutubeMusic)

# create widgets for sidebar
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

startDate_select = st.sidebar.date_input("Start Date:",
                                         value=endDate - datetime.timedelta(days=14),
                                         min_value=datetime.date(2021, 8, 25),
                                         max_value=datetime.date.today(),
                                         help="Select the start date for visualization")
endDate_select = st.sidebar.date_input("End Date:",
                                       value= endDate,
                                       min_value=datetime.date(2021, 8, 25),
                                       max_value=datetime.date.today(),
                                       help="Select the end date for visualization")
if startDate_select > endDate_select:
    st.error("Selected start date is larger than the selected end date")

st.sidebar.markdown("***")
st.sidebar.write("Options for Sentiment Analysis Visualization")

startDateSA_select = st.sidebar.date_input("Start Date:",
                                           value=endDate - datetime.timedelta(days=14),
                                           min_value=datetime.date(2021, 8, 25),
                                           max_value=datetime.date.today(),
                                           help="Select the start date for visualization",
                                           key="Sentiment Analysis Start Date Visualization")
endDateSA_select = st.sidebar.date_input("End Date:",
                                         value= endDate,
                                         min_value=datetime.date(2021, 8, 25),
                                         max_value=datetime.date.today(),
                                         help="Select the end date for visualization",
                                         key="Sentiment Analysis Start Date Visualization")
if startDateSA_select > endDateSA_select:
    st.error("Selected start date is larger than the selected end date")

st.sidebar.markdown("***")
st.sidebar.write("Options for WordCloud Visualization")
wordcloudPolarity_option = st.sidebar.selectbox(
    "Select Sentiment Polarity for Visualization:",
    ['Positive', 'Neutral', 'Negative'],
    help="Choose Sentiment Polarity desired for WordCloud Visualization"
)

ngramValue_option = st.sidebar.selectbox(
    "Choose the value for N-Gram",
    ('unigram', 'bigram', 'trigram'),
    help="Choose the value for N-Gram Frequency"
)

st.title("Social Media Dashboard")

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

    network_target = network_Spotify
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

    network_target = network_AppleMusic
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

    network_target = network_YoutubeMusic

# create the dashboard title
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
st.title("Social Media Campaigns and Metrics")
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

col_topMention, col_topHashtag = st.columns(2)
# Top Mentioned Account metrics
with col_topMention:
    st.subheader(f"{accName}'s Top Mentions")
    expander_topMention = st.expander(label='Set Conditions')
    with expander_topMention:
        topMention_num = st.slider("Display how many top mention users?", min_value=0, max_value=10, value=3)
    topMention_df = func.get_topMention(timeline_target)
    topMention_df = topMention_df.loc[:topMention_num - 1, :]
    st.dataframe(topMention_df)

# Top Hashtags metrics
with col_topHashtag:
    st.subheader(f"{accName}'s Top Hashtags")
    expander_topHashtag = st.expander(label='Set Conditions')
    with expander_topHashtag:
        topHashtag_num = st.slider("Display how many top hashtags?", min_value=0, max_value=10, value=3)
    topHashtag_df = func.get_topHashtag(timeline_target)
    topHashtag_df = topHashtag_df.loc[:topHashtag_num - 1, :]
    st.dataframe(topHashtag_df)

empty_col1, col_topDoC, empty_col3 = st.columns([5, 10, 5])
# Top degree of centrality for followers and friends metrics
with col_topDoC:
    st.subheader(f"{accName}'s Top Degree of Centrality")
    expander_topDOC = st.expander(label='Set Conditions')
    with expander_topDOC:
        DOC_option = st.selectbox(
            "Degree of Centrality for Followers or Friends?",
            ("Followers", "Friends")
        )
        topDoC_num = st.slider("Display how many users?", min_value=0, max_value=10, value=3, key='DoC_Followers')
    st.write(f"{DOC_option} Top Degree of Centrality")
    if DOC_option == "Followers":
        topDoC_Followers = func.get_topFollowerDoC(followers_target)
        topDoC_Followers = topDoC_Followers.loc[:topDoC_num - 1, :]
        topDoC_Followers
    elif DOC_option == "Friends":
        topDoC_Friends = func.get_topFriendDoC(friends_target)
        topDoC_Friends = topDoC_Friends.loc[:topDoC_num - 1, :]
        topDoC_Friends

func.emptyLine()

col_engagementTweetType, col_engagementTimeType, col_engagementBrandMention = st.columns(3)
# Average engagement based on types of tweet metric
with col_engagementTweetType:
    st.subheader(f"{accName}'s Average Engagement Based on Tweet Type")
    expander_engagementTweetType = st.expander(label='Set Conditions')
    with expander_engagementTweetType:
        days_select_E1 = st.number_input("Enter number of days:", min_value=0, value=7, step=1, key="num_tweetType_days")

        engagement_tweetType_df = func.engagement_tweetType(timeline_target, days_select_E1)

        TWEET_TYPE = engagement_tweetType_df['Tweet_Type'].unique()
        TWEET_TYPE_SELECTED = st.multiselect("Select the Tweet Type", TWEET_TYPE, default=TWEET_TYPE, key="select_tweetType")

        ENGAGEMENT_TYPE_1 = engagement_tweetType_df['Engagement'].unique()
        ENGAGEMENT_SELECTED_1 = st.multiselect("Select the Engagements", ENGAGEMENT_TYPE_1, default=ENGAGEMENT_TYPE_1, key="select_tweetType_engagement")
    days_select_E1 = int(days_select_E1)
    st.write(f"The average engagement for the last {days_select_E1} days")

    # dataframe filtering based on selected conditions
    mask_tweetType = engagement_tweetType_df['Tweet_Type'].isin(TWEET_TYPE_SELECTED)
    engagement_tweetType_df = engagement_tweetType_df[mask_tweetType]
    mask_engagementTweetType = engagement_tweetType_df['Engagement'].isin(ENGAGEMENT_SELECTED_1)
    engagement_tweetType_df = engagement_tweetType_df[mask_engagementTweetType]
    # checkbox to display dataframe
    tick_tweetType = st.checkbox("Display Engagement Dataframe", key="Tick for Tweet Type Engagement Table")
    if tick_tweetType:
        st.dataframe(engagement_tweetType_df)
    st.write("")

    #visualization
    func.drawGraph_engagementTweetType(engagement_tweetType_df)

# average engagement based on time of the day
with col_engagementTimeType:
    st.subheader(f"{accName}'s Average Engagement Based on Time Posted")
    expander_engagementTimeType = st.expander(label='Set Conditions')
    with expander_engagementTimeType:
        days_select_E2 = st.number_input("Enter number of days:", min_value=0, value=7, step=1, key="num_time_days")

        engagement_time_df = func.engagement_timeBin(timeline_target, days_select_E2)

        TIME_BIN = engagement_time_df['Time_Bin'].unique()
        TIME_BIN_SELECTED = st.multiselect("Select the Time Bin", TIME_BIN, default=TIME_BIN, key="select_timeBin")

        ENGAGEMENT_TYPE_2 = engagement_time_df['Engagement'].unique()
        ENGAGEMENT_SELECTED_2 = st.multiselect("Select the Engagements", ENGAGEMENT_TYPE_2, default=ENGAGEMENT_TYPE_2, key="select_time_engagement")
    days_select_E2 = int(days_select_E2)
    st.write(f"The average engagement for the last {days_select_E2} days")

    # dataframe filtering based on selected conditions
    mask_timeBin = engagement_time_df['Time_Bin'].isin(TIME_BIN_SELECTED)
    engagement_time_df = engagement_time_df[mask_timeBin]
    mask_engagementTime = engagement_time_df['Engagement'].isin(ENGAGEMENT_SELECTED_2)
    engagement_time_df = engagement_time_df[mask_engagementTime]
    # checkbox to display dataframe
    tick_timeBin = st.checkbox("Display Engagement Dataframe", key="Tick for Time Bin Engagement Table")
    if tick_timeBin:
        st.dataframe(engagement_time_df)
    st.write("")

    # visualization
    func.drawGraph_engagementTime(engagement_time_df)

# average engagement based on popular brand mention
with col_engagementBrandMention:
    st.subheader(f"{accName}'s Average Engagement Based on Popular Brand Mention")
    expander_engagementBrandMention = st.expander(label='Set Conditions')
    with expander_engagementBrandMention:
        days_select_E3 = st.number_input("Enter number of days:", min_value=0, value=7, step=1, key="num_brand_days")
    days_select_E3 = int(days_select_E3)
    st.write(f"The average engagement for the last {days_select_E3} days")
    engagementBrandMention = func.engagement_BrandMention(df_brandMention, days_select_E3)
    # checkbox to display dataframe
    tick_BrandMention = st.checkbox("Display Engagement Dataframe", key="Tick for Brand Mention Engagement Table")
    if tick_BrandMention:
        st.dataframe(engagementBrandMention)
    st.write("")

    # visualization
    func.drawGraph_engagementBrandMention(engagementBrandMention)

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
    st.subheader(f"{accName}'s Average Growth Rate")
    growthRate_layer, growthRate_df = func.growthRate(accName, df_target, startDate_select, endDate_select)
    tick_growthRate = st.checkbox("Display Average Growth Rate Dataframe", key="Tick for Average Growth Rate Table")
    if tick_growthRate:
        st.dataframe(growthRate_df)
    st.write("")
    st.altair_chart(growthRate_layer, use_container_width=True)
func.emptyLine()

# Assignment 2 Section
st.title("Social Media Sentiment Analysis")

col_pieChartSA, col_lineChartSA = st.columns(2)
sentimentAnalysis_df = func.getSentimentAnalysis(df_brandMention)
with col_pieChartSA:
    st.subheader(f"{accName}'s Overall Sentiment Analysis")
    func.getPieChart_SA(sentimentAnalysis_df)

with col_lineChartSA:
    st.subheader(f"{accName}'s Daily Sentiment Analysis")
    dailySA_layer, dailySA_df = func.dailySentimentAnalysisGraph(sentimentAnalysis_df, accName, startDateSA_select, endDateSA_select)
    st.altair_chart(dailySA_layer, use_container_width=True)
    tick_dailySA = st.checkbox("Display Daily Sentiment Analysis Dataframe", key="Tick for Daily Sentiment Analysis Table")
    if tick_dailySA:
        st.dataframe(dailySA_df)
func.emptyLine()

filteredSA_df = func.getFilterSA_dataframe(sentimentAnalysis_df, wordcloudPolarity_option)
wordcloudPolarity_graph, df_polarityTermCount = func.getWordCloud(filteredSA_df, ngramValue_option)
col_temp1, col_temp2 = st.columns(2)
with col_temp1:
    st.subheader(f"{accName}'s {wordcloudPolarity_option} Polarity WordCloud")
    plt.imshow(wordcloudPolarity_graph, interpolation='bilinear')
    plt.axis("off")
    plt.show()
    st.pyplot()
with col_temp2:
    st.subheader(f"{accName}'s {wordcloudPolarity_option} Polarity Term Frequency")
    expander_termFrequency = st.expander(label='Set Conditions')
    with expander_termFrequency:
        termFrequency_count = st.slider("Display how many top terms?", min_value=0, max_value=15, value=5)
    # checkbox to display dataframe
    tick_termFrequency = st.checkbox("Display Term Frequency Dataframe", key="Tick for Polarity Term Frequency Table")
    if tick_termFrequency:
        st.dataframe(df_polarityTermCount.head(termFrequency_count))
    func.termFrequency_Visualization(df_polarityTermCount.head(termFrequency_count), accName)
func.emptyLine()

# Assignment 3 Section
st.title("Social Media Network Analysis")

# get each company network data(node information and centrality measures)
networkData_df = func.getNetworkData(accName)

st.subheader(f"{accName}'s Network Visualization and Info")

col_networkVisualization, col_networkStats_left, col_networkStats_right = st.columns([10, 5, 5])
with col_networkVisualization:
    func.display_network(accName)

net_density, net_num_nodes, net_num_edges, net_num_communities, net_diameter = func.getNetworkInfo(network_target, networkData_df)
with col_networkStats_left:
    st.markdown('####')
    st.metric(label="Network Number Of Nodes:", value=net_num_nodes)
    st.metric(label="Network Number Of Edges:", value=net_num_edges)
    st.metric(label="Network Diameter:", value=net_diameter)
with col_networkStats_right:
    st.markdown('####')
    st.metric(label="Network Density:", value=net_density)
    st.metric(label="Number of Communities:", value=net_num_communities)
func.emptyLine()

col_networkCentralityMeasure, col_networkTopCommunity = st.columns(2)
with col_networkCentralityMeasure:
    st.subheader(f"{accName}'s Network Top Centrality Measures")
    expander_networkTopMeasures = st.expander(label='Set Conditions')

    networkData_colList = networkData_df.columns.tolist()
    networkData_colList = networkData_colList[8:12]

    with expander_networkTopMeasures:
        topMeasures_num = st.slider("Display how many top centrality measures users?", min_value=0, max_value=10, value=3)
        centralityMeasures_select = st.selectbox(
            "Select Centrality Measures",
            networkData_colList,
            index= 1,
            help="Choose Centrality Measures to display"
        )
    NetworkCentralityMeasures_df = func.getNetworkCentralityMeasures(networkData_df, centralityMeasures_select)
    NetworkCentralityMeasures_df = NetworkCentralityMeasures_df.head(topMeasures_num)
    st.dataframe(NetworkCentralityMeasures_df)

with col_networkTopCommunity:
    st.subheader(f"{accName}'s Network Community")
    expander_communitySize = st.expander(label='Set Conditions')
    with expander_communitySize:
        topCommunity_num = st.slider("Display how many top community?", min_value=0, max_value=10, value=3)

    df_communitySize = func.getCommunitySize(networkData_df)
    df_communitySize = df_communitySize.head(topCommunity_num)
    st.dataframe(df_communitySize.style.format({'community_size_percentage': '{:.2f}'}))

func.emptyLine()