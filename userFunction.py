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
import warnings
import csv
import matplotlib.pyplot as plt

import nltk
from nltk.tokenize import TweetTokenizer
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from nltk.corpus import sentiwordnet as swn
import re
import emoji
import string
from wordcloud import WordCloud
from textblob import TextBlob
import gensim
from gensim import corpora
import pyLDAvis.gensim_models

import networkx as nx
from operator import itemgetter
import community
import streamlit.components.v1 as components
from pyvis.network import Network

warnings.filterwarnings('ignore')

# create a line in the dashboard to seperate between different sections
def emptyLine():
    st.markdown("***")

# function to get the current and previous date used in the first section
def getDate(endDate):
    today = endDate  # current date and time
    yesterday = today - datetime.timedelta(days=1)
    date_today = today.strftime("%Y-%m-%d")
    date_yesterday = yesterday.strftime("%Y-%m-%d")
    return date_today, date_yesterday

# get the data to each company twitter profile images
@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def getprofileImg(df_profile):
    df = df_profile.copy()
    img = df.iloc[-1]['profile_img']
    return img

# get the user profile data for each company
@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def getuserProfile(screen_name):
    fName = "datasets/{}/user_profile.csv".format(screen_name)
    df = pd.read_csv(fName)

    # change the created at data to Malaysia time
    df['created_at'] = df['created_at'].astype('datetime64')
    df['created_at'] = df['created_at'].dt.tz_localize('UTC')
    df['created_at'] = df['created_at'].dt.tz_convert(pytz.timezone('Asia/Kuala_Lumpur'))
    return df

# get followers profile data for each company
@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def getfollowersProfile(accName):
    fName = "datasets/{}/followers.csv".format(accName)
    df_followers = pd.read_csv(fName)

    # change the created at data to Malaysia time
    df_followers['created_at'] = df_followers['created_at'].astype('datetime64')
    df_followers['created_at'] = df_followers['created_at'].dt.tz_localize('UTC')
    df_followers['created_at'] = df_followers['created_at'].dt.tz_convert(pytz.timezone('Asia/Kuala_Lumpur'))
    return df_followers

# get the company friends profile data
@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def getfriendsProfile(accName):
    fName = "datasets/{}/friends.csv".format(accName)
    df_friends = pd.read_csv(fName)

    # convert the created_at data to Malaysia time
    df_friends['created_at'] = df_friends['created_at'].astype('datetime64')
    df_friends['created_at'] = df_friends['created_at'].dt.tz_localize('UTC')
    df_friends['created_at'] = df_friends['created_at'].dt.tz_convert(pytz.timezone('Asia/Kuala_Lumpur'))

    return df_friends

# get the company's user timeline
@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def getuserTimeline(screen_name):
    fName = "datasets/{}/user_timeline.csv".format(screen_name)
    df_timeline = pd.read_csv(fName)

    # change the created_at data to Malaysia time
    df_timeline['created_at'] = df_timeline['created_at'].astype('datetime64')
    df_timeline['created_at'] = df_timeline['created_at'].dt.tz_localize('UTC')
    df_timeline['created_at'] = df_timeline['created_at'].dt.tz_convert(pytz.timezone('Asia/Kuala_Lumpur'))
    return df_timeline

# get mutual friends of the company
@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def getmutualFriends(df_friends, df_followers):
    df1 = df_friends.copy()
    df1.rename(columns={
        'friends_screen_name': 'screen_name'
    }, inplace=True)
    df2 = df_followers.copy()
    df2.rename(columns={
        'followers_screen_name': 'screen_name'
    }, inplace=True)
    # using pandas merge to see the overlapping value in the company's friends and followers dataframe
    df = pd.merge(df1, df2, how='inner', on=['screen_name'])
    df.drop(columns=['created_at_y', 'friends_count_y', 'followers_count_y', 'tweet_count_y'], inplace=True)
    df.rename(columns={
        'created_at_x': 'created_at',
        'friends_count_x': 'friends_count',
        'followers_count_x': 'followers_count',
        'tweet_count_x': 'tweet_count'
    }, inplace=True)
    return df

# get popular brand mention of the company
def getbrand_Mention(screen_name):
    fName = "datasets/{}/brand_mention.csv".format(screen_name)
    df = pd.read_csv(fName)

    # change the created_at data to Malaysia time
    df['created_at'] = df['created_at'].astype('datetime64')
    df['created_at'] = df['created_at'].dt.tz_localize('UTC')
    df['created_at'] = df['created_at'].dt.tz_convert(pytz.timezone('Asia/Kuala_Lumpur'))
    return df

# get the metrics for the first section
def getKPI(df, date_today, date_yesterday):
    # get the followers count today
    followers_num_today = df.loc[df['date'] == date_today, 'followers_count'].iloc[0]
    followers_num = int(followers_num_today)
    # get the followers count difference
    followers_num_yesterday = df.loc[df['date'] == date_yesterday, 'followers_count'].iloc[0]
    followers_diff = int(followers_num_today) - int(followers_num_yesterday)

    # get the friends count today
    friends_num_today = df.loc[df['date'] == date_today, 'friends_count'].iloc[0]
    friends_num = int(friends_num_today)
    # get the friends count difference
    friends_num_yesterday = df.loc[df['date'] == date_yesterday, 'friends_count'].iloc[0]
    friends_diff = int(friends_num_today) - int(friends_num_yesterday)

    # get the tweets count today
    tweet_num_today = df.loc[df['date'] == date_today, 'num_of_tweet'].iloc[0]
    tweet_num = int(tweet_num_today)
    # get the tweets count difference
    tweet_num_yesterday = df.loc[df['date'] == date_yesterday, 'num_of_tweet'].iloc[0]
    tweet_diff = int(tweet_num_today) - int(tweet_num_yesterday)

    # get the favorites count today
    fav_num_today = df.loc[df['date'] == date_today, 'favourite_count'].iloc[0]
    fav_num = int(fav_num_today)
    # get the favorites count difference
    fav_num_yesterday = df.loc[df['date'] == date_yesterday, 'favourite_count'].iloc[0]
    fav_diff = int(fav_num_today) - int(fav_num_yesterday)

    return followers_num, followers_diff, friends_num, friends_diff, tweet_num, tweet_diff, fav_num, fav_diff

# get the top mention metric
def get_topMention(df_timeline):
    df = df_timeline.copy()
    df.drop(columns=['tweet_content', 'created_at', 'hashtags', 'media_type', 'urls', 'quote_retweet_status'],
            inplace=True)
    df['user_mention'] = df['user_mention'].astype('str')
    df = df.groupby(['user_mention']).agg(['sum', 'count'])
    df.reset_index(inplace=True)
    df['count'] = df['favorite_count']['count']
    # find the average engagement
    df['retweet_average'] = df['retweet_count']['sum'] / df['retweet_count']['count']
    df['favorite_average'] = df['favorite_count']['sum'] / df['favorite_count']['count']
    df['retweet_average'] = df['retweet_average'].round()
    df['favorite_average'] = df['favorite_average'].round()
    df['retweet_average'] = df['retweet_average'].astype('int')
    df['favorite_average'] = df['favorite_average'].astype('int')

    df.drop(columns=['retweet_count', 'favorite_count'], axis=1, inplace=True)

    # preprocess the username text data
    df['user_mention'] = df['user_mention'].str.replace("[", "")
    df['user_mention'] = df['user_mention'].str.replace("'", "")
    df['user_mention'] = df['user_mention'].str.replace("]", "")
    df['user_mention'] = df['user_mention'].str.replace(",", "")
    df.sort_values(by='count', ascending=False, inplace=True)
    df['user_mention'] = df['user_mention'].replace('', np.nan)

    # remove empty value in the user mention column
    df = df.dropna(how='any')
    df.reset_index(inplace=True, drop=True)
    df['user_mention'] = '@' + df['user_mention'].astype(str)

    #for visualization since returning directly to streamlit has bugs on the display of the dataframe
    user_mention = df['user_mention'].tolist()
    count = df['count'].tolist()
    retweet_average = df['retweet_average'].tolist()
    favorite_average = df['favorite_average'].tolist()

    df_new = pd.DataFrame({
        'user_mention': user_mention,
        'count': count,
        'retweet_avg': retweet_average,
        'favorite_avg': favorite_average
    })
    return df_new

# get the top hashtag metric
def get_topHashtag(df_timeline):
    df = df_timeline.copy()
    df.drop(columns=['tweet_content', 'created_at', 'user_mention', 'media_type', 'urls', 'quote_retweet_status'],
            inplace=True)
    df['hashtags'] = df['hashtags'].astype('str')
    df = df.groupby(['hashtags']).agg(['sum', 'count'])
    df.reset_index(inplace=True)
    df['count'] = df['favorite_count']['count']
    # find the average engagement
    df['retweet_average'] = df['retweet_count']['sum'] / df['retweet_count']['count']
    df['favorite_average'] = df['favorite_count']['sum'] / df['favorite_count']['count']
    df['retweet_average'] = df['retweet_average'].round()
    df['favorite_average'] = df['favorite_average'].round()
    df['retweet_average'] = df['retweet_average'].astype('int')
    df['favorite_average'] = df['favorite_average'].astype('int')

    df.drop(columns=['retweet_count', 'favorite_count'], axis=1, inplace=True)

    # preprocess the username text data
    df['hashtags'] = df['hashtags'].str.replace("[", "")
    df['hashtags'] = df['hashtags'].str.replace("'", "")
    df['hashtags'] = df['hashtags'].str.replace("]", "")
    df['hashtags'] = df['hashtags'].str.replace(",", "")
    df.sort_values(by='count', ascending=False, inplace=True)
    df['hashtags'] = df['hashtags'].replace('', np.nan)

    # remove empty value in the user mention column
    df.dropna(how='any', inplace=True)
    df.reset_index(inplace=True, drop=True)
    df['hashtags'] = '#' + df['hashtags'].astype(str)

    # for visualization since returning directly to streamlit has bugs on the display of the dataframe
    hashtags = df['hashtags'].tolist()
    count = df['count'].tolist()
    retweet_average = df['retweet_average'].tolist()
    favorite_average = df['favorite_average'].tolist()

    df_new = pd.DataFrame({
        'hashtags': hashtags,
        'count': count,
        'retweet_avg': retweet_average,
        'favorite_avg': favorite_average
    })
    return df_new

# get the top Degree of Centrality for the company's followers
def get_topFollowerDoC(df_followers):
    df = df_followers.copy()
    df['count'] = df['friends_count'] + df['followers_count']
    #df.drop(columns=['created_at','friends_count','followers_count','tweet_count'],inplace=True)
    df = df[['followers_screen_name','count']]
    df.sort_values(by='count', inplace=True, ascending=False)
    df.reset_index(inplace=True, drop=True)
    return df

# get the top Degree of Centrality for the company's friends
def get_topFriendDoC(df_friends):
    df = df_friends.copy()
    df['count'] = df['friends_count'] + df['followers_count']
    df.drop(columns=['created_at', 'friends_count', 'followers_count', 'tweet_count'], inplace=True)
    df.sort_values(by='count', inplace=True, ascending=False)
    df.reset_index(inplace=True, drop=True)
    return df

# get the average engagement based on tweet types metric
def engagement_tweetType(df, days_select):
    # renaming the value
    df.loc[df['media_type'] == "no_media", 'media_type'] = "text_only"
    df.loc[df['media_type'] == "photo", 'media_type'] = "text_and_photo"
    df.loc[df['media_type'] == "video", 'media_type'] = "text_and_video"
    df.loc[df['media_type'] == "animated_gif", 'media_type'] = "text_and_animated_gif"
    endDate = datetime.datetime.now()
    startDate = endDate - datetime.timedelta(days=days_select)
    df = df.loc[:,['created_at','retweet_count','favorite_count','media_type']]
    # select the data within the specified range of date from the widget input
    df['created_at'] = pd.to_datetime(df.created_at).dt.tz_localize(None)
    mask = (df['created_at'] >= startDate) & (df['created_at'] <= endDate)
    df = df.loc[mask]
    df = df.rename(columns={'media_type': 'tweet_type'})
    df = df.groupby(['tweet_type']).agg(['sum', 'count'])
    df.reset_index(inplace=True)
    # calculate the average engagement
    df['retweet_average'] = df['retweet_count']['sum'] / df['retweet_count']['count']
    df['favorite_average'] = df['favorite_count']['sum'] / df['favorite_count']['count']
    df.drop(columns = ['retweet_count', 'favorite_count'], axis=1, inplace=True)
    df = df.melt(id_vars='tweet_type').rename(columns=str.title)
    df.drop(columns = ['Variable_1'], axis=1, inplace=True)
    df.rename(columns={'Variable_0': 'Engagement'}, inplace=True)
    df['Value'] = df['Value'].round()

    # create dataframe included all the tweet type although it might not appear within the range of date
    if ('text_only' not in df['Tweet_Type']) and ('retweet_average' not in df['Engagement']):
        df.loc[len(df.index)] = ['text_only', 'retweet_average', 0]
    if ('text_only' not in df['Tweet_Type']) and ('favorite_average' not in df['Engagement']):
        df.loc[len(df.index)] = ['text_only', 'favorite_average', 0]
    if ('text_and_video' not in df['Tweet_Type']) and ('retweet_average' not in df['Engagement']):
        df.loc[len(df.index)] = ['text_and_video', 'retweet_average', 0]
    if ('text_and_video' not in df['Tweet_Type']) and ('favorite_average' not in df['Engagement']):
        df.loc[len(df.index)] = ['text_and_video', 'favorite_average', 0]
    if ('text_and_photo' not in df['Tweet_Type']) and ('retweet_average' not in df['Engagement']):
        df.loc[len(df.index)] = ['text_and_photo', 'retweet_average', 0]
    if ('text_and_photo' not in df['Tweet_Type']) and ('favorite_average' not in df['Engagement']):
        df.loc[len(df.index)] = ['text_and_photo', 'favorite_average', 0]
    if ('text_and_animated_gif' not in df['Tweet_Type']) and ('retweet_average' not in df['Engagement']):
        df.loc[len(df.index)] = ['text_and_animated_gif', 'retweet_average', 0]
    if ('text_and_animated_gif' not in df['Tweet_Type']) and ('favorite_average' not in df['Engagement']):
        df.loc[len(df.index)] = ['text_and_animated_gif', 'favorite_average', 0]
    df.drop_duplicates(subset=['Tweet_Type', 'Engagement'], inplace=True)

    df.sort_values(by="Tweet_Type", inplace=True, ascending=False)
    df['Value'] = df['Value'].astype('int')
    df.reset_index(inplace=True, drop=True)
    return df

# create average engagement based on time posted metric
def engagement_timeBin(df, days_select):
    endDate = datetime.datetime.now()
    startDate = endDate - datetime.timedelta(days=days_select)

    # define the bins
    # reference: https://www.learnersdictionary.com/qa/parts-of-the-day-early-morning-late-morning-etc
    bins = [0, 5, 12, 17, 21, 24]
    # add custom labels
    labels = ['night_1', 'morning', 'afternoon', 'evening', 'night']

    # labeling the part of the day based on the created_at data
    df = df.loc[:, ['created_at', 'retweet_count', 'favorite_count', 'tweet_content']]
    df['time_bin'] = pd.cut(df.created_at.dt.hour, bins, labels=labels, right=False)
    df = df.loc[(df['favorite_count'] != 0) | (~df['tweet_content'].str.contains("RT"))]
    df.drop(columns=['tweet_content'], axis=1, inplace=True)
    df['time_bin'] = df['time_bin'].replace({'night_1': 'night'})
    df['created_at'] = pd.to_datetime(df.created_at).dt.tz_localize(None)
    mask = (df['created_at'] >= startDate) & (df['created_at'] <= endDate)
    df = df.loc[mask]

    df = df.groupby(['time_bin']).agg(['sum', 'count'])
    df.reset_index(inplace=True)
    # calculate the average engagement
    df['retweet_average'] = df['retweet_count']['sum'] / df['retweet_count']['count']
    df['favorite_average'] = df['favorite_count']['sum'] / df['favorite_count']['count']
    df.drop(columns=['retweet_count', 'favorite_count'], axis=1, inplace=True)
    df = df.melt(id_vars='time_bin').rename(columns=str.title)
    df.drop(columns=['Variable_1'], axis=1, inplace=True)
    df.rename(columns={'Variable_0': 'Engagement'}, inplace=True)
    df['Value'] = df['Value'].fillna(0)
    df['Value'] = df['Value'].round()

    df_mapping = pd.DataFrame({
        'time_bin': ['morning', 'afternoon', 'evening', 'night'],
    })
    sort_mapping = df_mapping.reset_index().set_index('time_bin')
    df['time_bin_num'] = df['Time_Bin'].map(sort_mapping['index'])
    df.sort_values(by='time_bin_num', inplace=True, ascending=True)
    df.drop(['time_bin_num'], axis=1, inplace=True)
    df.reset_index(inplace=True, drop=True)
    df['Time_Bin'] = df['Time_Bin'].astype('str')
    df['Value'] = df['Value'].astype('int')
    return df

# get the average engagement based on popular brand mention metric
def engagement_BrandMention(df_brandMention, days_select):
    endDate = datetime.datetime.now()
    startDate = endDate - datetime.timedelta(days=days_select)
    df = df_brandMention.copy()
    # filter the dataframe within the range of date
    df['created_at'] = pd.to_datetime(df.created_at).dt.tz_localize(None)
    mask = (df['created_at'] >= startDate) & (df['created_at'] <= endDate)
    df = df.loc[mask]
    df.reset_index(inplace=True, drop=True)
    # calculate the average engagement
    retweet_average = df['retweet_count'].sum() / len(df)
    favorite_average = df['favorite_count'].sum() / len(df)
    engagementName = ['retweet_average', 'favorite_average']
    engagementValue = [retweet_average, favorite_average]
    df_new = pd.DataFrame({
        'Engagement': engagementName,
        'Value': engagementValue
    })
    df_new['Value'] = df_new['Value'].fillna(0)
    df_new['Value'] = df_new['Value'].round()
    df_new['Value'] = df_new['Value'].astype('int')
    return df_new

# draw the visualization for engagement based on tweet types
def drawGraph_engagementTweetType(engagement_df):
    bars = alt.Chart(engagement_df).mark_bar(
        cornerRadiusTopLeft=3,
        cornerRadiusTopRight=3
    ).encode(
        x=alt.X('Engagement:N', title=None),
        y=alt.Y('Value:Q', axis=alt.Axis(ticks=False, labels=False)),
        color='Engagement:N'
    )

    text = bars.mark_text(
        align='center',
        baseline='middle',
        dy=-10,
        fontWeight='bold'
    ).encode(
        text='Value'
    )

    layer = alt.layer(bars, text, data=engagement_df).facet(
        column='Tweet_Type:N'
    ).configure_axis(
        domainWidth=0.8,
        offset=2,
        labelFontWeight='bold'
    ).configure_view(
        stroke='transparent'
    ).configure_header(
        labelOrient='left',
        labelFontWeight='bold',
        title=None
    ).configure_legend(
        disable=True
    )
    return st.altair_chart(layer, use_container_width=True)

# draw the visualization for engagement based on time posted
def drawGraph_engagementTime(engagement_df):
    bars = alt.Chart(engagement_df).mark_bar(
        cornerRadiusTopLeft=3,
        cornerRadiusTopRight=3
    ).encode(
        x=alt.X('Engagement:N', title=None),
        y=alt.Y('Value:Q', axis=alt.Axis(ticks=False, labels=False)),
        color='Engagement:N'
    )

    text = bars.mark_text(
        align='center',
        baseline='middle',
        dy=-10,
        fontWeight='bold'
    ).encode(
        text='Value'
    )

    layer = alt.layer(bars, text, data=engagement_df).facet(
        column='Time_Bin:N'
    ).configure_axis(
        domainWidth=0.8,
        offset=2,
        labelFontWeight='bold'
    ).configure_view(
        stroke='transparent'
    ).configure_header(
        labelOrient='left',
        labelFontWeight='bold',
        title=None
    ).configure_legend(
        disable=True
    )
    return st.altair_chart(layer, use_container_width=True)

# draw the visualization for engagement based on popular brand mention
def drawGraph_engagementBrandMention(engagement_df):
    bars = alt.Chart(engagement_df).mark_bar(width=20).encode(
        x=alt.X('Engagement:N', title=None),
        y=alt.Y('Value:Q', axis=alt.Axis(labels=False)),
        color='Engagement:N'
    ).properties(
        title="Average Engagement"
    )


    text = bars.mark_text(
        align='center',
        baseline='middle',
        dy=20,
        dx=25,
        fontWeight='bold'
    ).encode(
        text='Value'
    )

    layer = alt.layer(bars, text, data=engagement_df).configure(
        autosize='fit'
    ).configure_axis(
        domainWidth=0.8,
        labelFontWeight='bold'
    ).configure_view(
        stroke='transparent'
    ).configure_header(
        labelOrient='left',
        labelFontWeight='bold',
        title=None
    ).configure_legend(
        disable=True
    ).properties(
        height=420
    )

    return st.altair_chart(layer, use_container_width=True)

# get the company demographic based on account creation date metric
def profileDemographic(screen_name, df_followers, df_friends, option, freq):
    if option == "followers":
        df = df_followers.copy()
        df = df[['created_at']]
    elif option == "friends":
        df = df_friends.copy()
        df = df.drop(['friends_screen_name', 'friends_count', 'followers_count', 'tweet_count'], axis=1)
    df["count"] = 1
    df = df.sort_values(by='created_at', ascending=True).reset_index(drop=True)
    df_new = df.copy()
    # change the created_at data to the selected period (Yearly, Quarterly, Monthly)
    df_new['created_at'] = df_new['created_at'].dt.to_period(freq)
    df_new = df_new.groupby(['created_at']).sum().reset_index()
    df_new['created_at'] = df_new['created_at'].astype('str')

    # Add missing date
    rng = pd.date_range(df.iloc[0]["created_at"], df.iloc[-1]["created_at"], freq=freq)
    df_time = pd.DataFrame({'created_at': rng})
    df_time['created_at'] = df_time['created_at'].dt.to_period(freq)
    df_time['created_at'] = df_time['created_at'].astype('str')
    df_time['count'] = 0

    result = pd.merge(df_time, df_new, how="outer", on="created_at")
    result["count_y"] = result["count_y"].replace(np.nan, 0).astype('int')
    result["count_x"] = result["count_x"].replace(np.nan, 0).astype('int')
    result["count"] = result["count_y"] + result["count_x"]
    result["count"] = result["count"].astype("int")
    result = result.drop(['count_x', 'count_y'], axis=1)

    # Altair visualization into horizontal bar chart
    bars = alt.Chart(result).mark_bar(
        cornerRadiusTopLeft=3,
        cornerRadiusTopRight=3
    ).encode(
        x='count',
        y='created_at'
    ).properties(
        title=f"{screen_name} followers account created"
    )

    text = bars.mark_text(
        align='left',
        baseline='middle',
        dx=3,
        fontWeight='bold'
    ).encode(
        text='count'
    )

    layer = alt.layer(bars, text).configure_view(
        stroke='transparent'
    ).configure_axis(
        grid=False
    )
    return st.altair_chart(layer, use_container_width=True)

# get the growth rate metric
def growthRate(screen_name, df, startDate_select, endDate_select):
    # calculate the growth rate based on the attribute
    # followers_count
    df['growth_rate_followers'] = df["followers_count"].pct_change()
    df['growth_rate_followers'] = (df["growth_rate_followers"] * 100).round(5)
    df['date'] = df['date'].astype('str')

    # friends_count
    df['growth_rate_friends'] = df["friends_count"].pct_change()
    df['growth_rate_friends'] = (df["growth_rate_friends"] * 100).round(5)
    df['date'] = df['date'].astype('str')

    # num_of_tweet
    df['growth_rate_tweet'] = df["num_of_tweet"].pct_change()
    df['growth_rate_tweet'] = (df["growth_rate_tweet"] * 100).round(5)
    df['date'] = df['date'].astype('str')

    # favourite_count
    df['growth_rate_favourite'] = df["favourite_count"].pct_change()
    df['growth_rate_favourite'] = (df["growth_rate_favourite"] * 100).round(5)
    df['date'] = df['date'].astype('str')

    df = df.fillna(0)

    df['date'] = pd.to_datetime(df['date'])
    startDate_select = pd.to_datetime(startDate_select)
    endDate_select = pd.to_datetime(endDate_select)
    mask = (df['date'] >= startDate_select) & (df['date'] <= endDate_select)
    df = df.loc[mask]
    df['date'] = df['date'].astype('str')

    # calculate average growth rate throughout the days
    st.write(f"The average of  growth rate for the last {len(df)} days:")
    average_GR_value = []
    average_GR_name = []
    # followers count
    average_GR_followers = math.pow((df.iloc[-1]['followers_count'] / df.iloc[0]['followers_count']), 1 / len(df)) - 1
    average_GR_followers = round(average_GR_followers * 100, 5)
    average_GR_value.append(average_GR_followers)
    average_GR_name.append("Followers Count")

    # friends count
    average_GR_friends = math.pow((df.iloc[-1]['friends_count'] / df.iloc[0]['friends_count']), 1 / len(df)) - 1
    average_GR_friends = round(average_GR_friends * 100, 5)
    average_GR_value.append(average_GR_friends)
    average_GR_name.append("Friends Count")

    # number of tweets
    average_GR_tweet = math.pow((df.iloc[-1]['num_of_tweet'] / df.iloc[0]['num_of_tweet']), 1 / len(df)) - 1
    average_GR_tweet = round(average_GR_tweet * 100, 5)
    average_GR_value.append(average_GR_tweet)
    average_GR_name.append("Tweet Count")

    # favorite count
    average_GR_favorite = math.pow((df.iloc[-1]['favourite_count'] / df.iloc[0]['favourite_count']), 1 / len(df)) - 1
    average_GR_favorite = round(average_GR_favorite * 100, 5)
    average_GR_value.append(average_GR_favorite)
    average_GR_name.append("Favorite Count")

    # display average GR value in dataframe
    df_avg_GR = pd.DataFrame({
        'Growth Rate': average_GR_name,
        'Average Value': average_GR_value
    })

    df.drop(['created_at', 'num_of_tweet','favourite_count', 'followers_count',
    'friends_count', 'profile_img'], axis=1, inplace=True)

    df = df.reset_index().melt(id_vars='date',
                               value_vars=['growth_rate_followers','growth_rate_friends',
                                           'growth_rate_tweet','growth_rate_favourite'],
                               var_name='category',
                               value_name='growth_rate')

    # st.dataframe(df)

    # Create a selection that chooses the nearest point & selects based on x-value
    nearest = alt.selection(type='single', nearest=True, on='mouseover',
                            fields=['date'], empty='none')

    # The basic line
    line = alt.Chart(df).mark_line(point=True).encode(
        x='date',
        y='growth_rate:Q',
        color='category:N'
    ).properties(
        title=f"{screen_name} Average Growth Rate"
    )

    # Transparent selectors across the chart. This is what tells us
    # the x-value of the cursor
    selectors = alt.Chart(df).mark_point().encode(
        x='date',
        opacity=alt.value(0),
    ).add_selection(
        nearest
    )

    # Draw points on the line, and highlight based on selection
    points = line.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    # Draw text labels near the points, and highlight based on selection
    text = line.mark_text(align='left', dx=5, dy=-5, fontWeight='bold').encode(
        text=alt.condition(nearest, 'growth_rate:Q', alt.value(' '))
    )

    # Draw a rule at the location of the selection
    rules = alt.Chart(df).mark_rule(color='gray').encode(
        x='date',
    ).transform_filter(
        nearest
    )

    # Put the five layers into a chart and bind the data
    layer = alt.layer(
        line, selectors, points, rules, text
    ).configure_view(
        stroke='transparent'
    ).configure_axis(
        grid=False
    ).configure_legend(
        columns=2,
        orient='bottom'
    )
    return layer, df_avg_GR

#####################################################################################

def preprocess_tweet(text):
    text = text.lower()
    text = re.sub('@[^\s]+', '', text)  # remove any user screen name
    text = re.sub(emoji.get_emoji_regexp(), r"", text)  # remove any emoji
    text = re.sub(r"http\S+", "", text)  # remove any web link
    text = re.sub(r'[^\x00-\x7F]', '', text)  # remove non-ascii character
    text = re.sub('\n', '', text)  # remove "\n"
    punct = string.punctuation
    punct = punct.replace("#", "")  # don't remove hashtag
    punct_pattern = r"[{}]".format(punct)  # create the regex pattern
    text = re.sub(punct_pattern, '', text)  # remove all punctuation symbol except '#'
    text = re.sub(r'\b[0-9]+\b\s*', '', text)  # remove words containing numbers only
    text = re.sub('(\\b[A-Za-z] \\b|\\b [A-Za-z]\\b)', '', text)  # remove single character in the text

    # tokenization
    tweet_tokenizer = TweetTokenizer()
    tokens = tweet_tokenizer.tokenize(text)

    # stop words removal
    stop_words = set(stopwords.words('english'))
    new_stopwords = ['rt', '#', 'amp']
    newstopwords = stop_words.union(new_stopwords)
    text = [word for word in tokens if not word in newstopwords]

    # remove single character word
    text = [word for word in text if len(word) > 1]

    # stemming the words
    ps = PorterStemmer()
    for index, word in enumerate(text):
        text[index] = ps.stem(word)

    merge_text = ""
    for i in reversed(range(len(text))):
        merge_text = str(text[i]) + " " + merge_text

    return merge_text

def generate_N_grams(text,ngram=1):
    words=[word for word in text.split()]
    temp=zip(*[words[i:] for i in range(0,ngram)])
    ans=[' '.join(ngram) for ngram in temp]
    return ans

def getFilterSA_dataframe(df_sa, option):
    df = df_sa.copy()
    option = option.lower()
    df = df[df['sentiment_score'] == option]
    df = df.reset_index(drop=True)
    return df

@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def getWordCloud(text_df, n_gram_option):
    df = text_df.copy()
    df = df[['tweet_content']]
    df['clean_tweet'] = df['tweet_content'].apply(preprocess_tweet)

    if n_gram_option == "unigram":
        n_gram_value = 1
    elif n_gram_option == "bigram":
        n_gram_value = 2
    elif n_gram_option == "trigram":
        n_gram_value = 3


    df['tweet_tokens'] = df.apply(lambda x: generate_N_grams(x['clean_tweet'], n_gram_value), axis=1)

    tf = Counter()
    for index, row in df.iterrows():
        word = row['tweet_tokens']
        tf.update(word)

    df_termCount = pd.DataFrame(columns=['terms', 'count'])
    for tag, count in tf.most_common(20):
        df_termCount = df_termCount.append({
            'terms': tag,
            'count': count
        }, ignore_index=True)
    df_termCount['count'] = df_termCount['count'].astype('int')
    df_termCount = df_termCount.sort_values(by=['count'], ascending=False, ignore_index=True)

    wordcloud_graph = WordCloud(background_color='white',
                                width=5000,
                                height=3000, # adjust later based on dataframe & graph column
                                max_words=20
                                ).generate_from_frequencies(tf)

    return wordcloud_graph, df_termCount

def termFrequency_Visualization(df, screen_name):
    bars = alt.Chart(df).mark_bar(
        cornerRadiusTopLeft=3,
        cornerRadiusTopRight=3
    ).encode(
        x='count',
        y= alt.Y('terms', sort=None)
    ).properties(
        title=f"{screen_name} Term Frequency"
    )

    text = bars.mark_text(
        align='left',
        baseline='middle',
        dx=3,
        fontWeight='bold'
    ).encode(
        text='count'
    )

    layer = alt.layer(bars, text).configure_view(
        stroke='transparent'
    ).configure_axis(
        grid=False
    )
    return st.altair_chart(layer, use_container_width=True)

def getSentimentScore(val):
    if val < 0:
        score = "negative"
    elif val == 0:
        score = "neutral"
    else:
        score = "positive"
    return score

def getSentimentAnalysis(df_text):
    df = df_text.copy()
    df = df[['created_at','tweet_content']]
    df['clean_tweet'] = df['tweet_content'].apply(preprocess_tweet)

    df['polarity'] = df['clean_tweet'].apply(lambda x: TextBlob(x).polarity)
    df['subjective'] = df['clean_tweet'].apply(lambda x: TextBlob(x).subjectivity)
    df['sentiment_score'] = df['polarity'].apply(getSentimentScore)

    return df

def getPieChart_SA(df_sa):
    df = df_sa.copy()
    valueCount_dict = df['sentiment_score'].value_counts().to_dict()
    totalVal_count = len(df)

    # sort the dictionary based on custom order
    keyorder = ['positive', 'neutral', 'negative']
    orderedList = sorted(valueCount_dict.items(), key=lambda i: keyorder.index(i[0]))

    cat_list, val_list = [], []
    for i in range(len(orderedList)):
        cat_list.append(orderedList[i][0])
        val_list.append(round((orderedList[i][1] / totalVal_count) * 100, 2))

    explode = (0.1, 0.1, 0.1)
    fig1, ax1 = plt.subplots()
    ax1.pie(val_list,
            labels=cat_list,
            explode=explode,
            colors=['mediumseagreen', 'gold', 'crimson'],
            autopct='%1.1f%%',
            shadow=True,
            startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    st.pyplot(fig1, clear_figure=True)

def dailySentimentAnalysisGraph(text_df, screen_name, startDate_select, endDate_select):
    df = text_df[['created_at', 'sentiment_score']].copy()
    df = df.sort_values(by='created_at', ascending=True).reset_index(drop=True)
    df['created_at'] = df['created_at'].dt.date
    df['created_at'] = df['created_at'].astype('str')
    df['created_at'] = pd.to_datetime(df['created_at'])
    startDate_select = pd.to_datetime(startDate_select)
    endDate_select = pd.to_datetime(endDate_select)
    mask = (df['created_at'] >= startDate_select) & (df['created_at'] <= endDate_select)
    df = df.loc[mask]
    df['created_at'] = df['created_at'].dt.date
    df['created_at'] = df['created_at'].astype('str')

    # add missing sentiment score categories
    start_date = df['created_at'].iloc[0]
    end_date = df['created_at'].iloc[-1]
    df_temp = pd.DataFrame({
        'created_at': pd.date_range(start=start_date, end=end_date, freq='D')
    })
    df_temp['created_at'] = df_temp['created_at'].dt.date
    df_temp['created_at'] = df_temp['created_at'].astype('str')
    categories = ['negative', 'neutral', 'positive']
    new_cat = []

    for i in range(len(df_temp)):
        for x in categories:
            new_cat.append(x)

    df_temp = df_temp.loc[df_temp.index.repeat(3)].reset_index(drop=True)
    df_temp['sentiment_score'] = new_cat
    df_temp['count'] = 0
    df = df.groupby(["created_at", "sentiment_score"]).size().reset_index(name="count")

    result = df.append(df_temp)
    result = result.drop_duplicates(subset=['created_at', 'sentiment_score'], keep='first')
    result = result.sort_values(by='created_at', ascending=True).reset_index(drop=True)
    result = result.rename(columns={
        'created_at': 'date',
        'sentiment_score': 'sentiment_category'
    })

    domain = ['positive', 'neutral', 'negative']
    range_ = ['green', 'orange', 'red']
    # Line graph visualization
    # Create a selection that chooses the nearest point & selects based on x-value
    nearest = alt.selection(type='single', nearest=True, on='mouseover',
                            fields=['date'], empty='none')

    # The basic line
    line = alt.Chart(result).mark_line(point=True).encode(
        x='date',
        y='count:Q',
        color=alt.Color('sentiment_category', scale=alt.Scale(domain=domain, range=range_))
    ).properties(
        title=f"{screen_name} Daily Sentiment Value"
    )

    # Transparent selectors across the chart. This is what tells us
    # the x-value of the cursor
    selectors = alt.Chart(result).mark_point().encode(
        x='date',
        opacity=alt.value(0),
    ).add_selection(
        nearest
    )

    # Draw points on the line, and highlight based on selection
    points = line.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    # Draw text labels near the points, and highlight based on selection
    text = line.mark_text(align='left', dx=5, dy=-5, fontSize=15, fontWeight='bold').encode(
        text=alt.condition(nearest, 'count:Q', alt.value(' '))
    )

    # Draw a rule at the location of the selection
    rules = alt.Chart(result).mark_rule(color='gray').encode(
        x='date',
    ).transform_filter(
        nearest
    )

    # Put the five layers into a chart and bind the data
    layer = alt.layer(
        line, selectors, points, rules, text
    ).configure_view(
        stroke='transparent'
    ).configure_axis(
        grid=False
    ).configure_legend(
        columns=3,
        orient='bottom'
    ).properties(
        height=350
    )

    sentiment_cat = ['negative', 'neutral', 'positive']
    final_result = pd.concat([result.set_index(['date']).groupby('sentiment_category')['count'].get_group(key) for key in sentiment_cat], axis=1)
    final_result.columns = sentiment_cat
    final_result.reset_index(inplace=True)

    return layer, final_result

def getTopicModeling(screen_name):
    fName = "datasets/{}/topicModel.csv".format(screen_name)
    df = pd.read_csv(fName)
    df = df.set_axis(['keyword1','keyword2','keyword3','keyword4','keyword5',
                      'keyword6','keyword7','keyword8','keyword9','keyword10'], axis=1, inplace=False)
    df = df.rename(index=lambda s: 'Topic'+ str(s+1))

    return df

######################################################################################
@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def getNetworkStats(screen_name):
    # read the node list dataset
    with open("datasets/{}/nodeList.csv".format(screen_name), 'r', encoding='utf-8') as nodecsv:
        nodereader = csv.reader(nodecsv)
        # Python list comprehension and list slicing to remove the header row)
        nodes = [n for n in nodereader][1:]

    node_names = [n[0] for n in nodes]  # Get a list names

    # read the edge list dataset
    with open("datasets/{}/edgeList.csv".format(screen_name), 'r', encoding='utf-8') as edgecsv:
        edgereader = csv.reader(edgecsv)
        edges = [tuple(e) for e in edgereader][1:]  # Why index 1? You try it with index 0

    # create graph object
    G = nx.Graph()

    # add lists of nodes and edges
    G.add_nodes_from(node_names)  # put the nodes into the graph object
    G.add_edges_from(edges)  # put the edges into the graph object
    # print("Graph Information: ", nx.info(G))

    # node information
    location_dict = {}
    created_at_dict = {}
    followers_count_dict = {}
    friends_count_dict = {}
    statuses_count_dict = {}

    for node in nodes:
        location_dict[node[0]] = node[1]
        created_at_dict[node[0]] = node[2]
        followers_count_dict[node[0]] = node[3]
        friends_count_dict[node[0]] = node[4]
        statuses_count_dict[node[0]] = node[5]

    # Add each dictionary as a node attribute to the Graph object
    nx.set_node_attributes(G, name='location', values=location_dict)
    nx.set_node_attributes(G, name='created_at', values=created_at_dict)
    nx.set_node_attributes(G, name='followers_count', values=followers_count_dict)
    nx.set_node_attributes(G, name='friends_count', values=friends_count_dict)
    nx.set_node_attributes(G, name='statuses_count', values=statuses_count_dict)

    # Calculating degree and adding it as an attribute to your network
    # while "degree" reports the sum of "in_degree" and "out_degree" even though that may feel inconsistent at times
    person_dict = dict(G.degree(G.nodes()))
    nx.set_node_attributes(G, name='person_dict', values=person_dict)

    return G

def display_network(accName):
    networkPyvis = open(f'datasets/{accName}_NetworkPyvis.html', 'r', encoding='utf-8')
    components.html(networkPyvis.read(), height=325)

def getNetworkInfo(network, network_df):
    density = round(nx.density(network), 5)
    num_nodes = nx.number_of_nodes(network)
    num_edges = nx.number_of_edges(network)

    communities_list = network_df['modularity'].tolist()
    num_communities = max(communities_list) + 1

    # diameter = nx.diameter(network)
    diameter = 4 #temp

    return density, num_nodes, num_edges, num_communities, diameter

def getNetworkData(accName):
    fName = "datasets/{}/networkData.csv".format(accName)
    df_network = pd.read_csv(fName)

    return df_network

def getNetworkCentralityMeasures(network_df, col_select):
    df = network_df.copy()
    df = df[['Id','degree','betweenness','closeness','eigenvector']]
    df = pd.melt(df, id_vars=['Id'], value_vars=['degree','betweenness','closeness','eigenvector'])
    # df.sort_values(by=['betweenness'], ascending=False, inplace=True)
    df = df.rename(columns={
        'Id': 'Screen Name',
        'variable': 'Centrality Measure',
        'value': 'Value'
    })
    df = df.loc[df['Centrality Measure'] == col_select]
    df.sort_values(by=['Value'], ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

def getCommunitySize(network_df):
    df = network_df.copy()
    df = df[['Id','betweenness','eigenvector','closeness','modularity']]
    community_size_series = df['modularity'].value_counts()
    community_size = community_size_series.to_dict()

    df['community_size'] = df['modularity'].map(community_size)
    df['community_size_percentage'] = (df['community_size'] / len(df)) * 100
    df['community_size_percentage'] = df['community_size_percentage'].round(2)

    df = df.sort_values(by=['betweenness','eigenvector','closeness'], ascending=False, ignore_index=True)
    df = df.drop_duplicates(subset=['modularity'], keep='first', ignore_index=True)
    df = df.drop(columns=['betweenness','eigenvector','closeness'])

    df = df.rename(columns={
        'Id': 'top_node',
        'modularity': 'community'
    })
    df = df[['community', 'top_node', 'community_size', 'community_size_percentage']]
    df = df.sort_values(by=['community_size'], ascending=False, ignore_index=True)
    df['community_size'] = df['community_size'].astype('str') + str(" (") + df['community_size_percentage'].astype('str') + str('%)')
    df = df.drop(columns=['community_size_percentage'])

    return df