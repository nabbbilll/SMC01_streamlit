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
    df.drop(columns=['created_at','friends_count','followers_count','tweet_count'],inplace=True)
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

# get the company demographic based on account creation date metric
def profileDemographic(screen_name, df_followers, df_friends, option, freq):
    if option == "followers":
        df = df_followers.copy()
        df = df.drop(['followers_screen_name', 'friends_count', 'followers_count', 'tweet_count'], axis=1)
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
def growthRate(screen_name, df, avg_rate, startDate_select, endDate_select):
    # calculate the growth rate based on the selected attribute
    if avg_rate == "followers_count":
        df['growth_rate_followers'] = df[avg_rate].pct_change()
        df['growth_rate_followers'] = (df["growth_rate_followers"] * 100).round(5)
        df['date'] = df['date'].astype('str')
        df = df.fillna(0)
        y_label = 'growth_rate_followers'
        y_name = 'followers count'
    elif avg_rate == "friends_count":
        df['growth_rate_friends'] = df[avg_rate].pct_change()
        df['growth_rate_friends'] = (df["growth_rate_friends"] * 100).round(5)
        df['date'] = df['date'].astype('str')
        df = df.fillna(0)
        y_label = 'growth_rate_friends'
        y_name = 'friends count'
    elif avg_rate == "num_of_tweet":
        df['growth_rate_tweet'] = df[avg_rate].pct_change()
        df['growth_rate_tweet'] = (df["growth_rate_tweet"] * 100).round(5)
        df['date'] = df['date'].astype('str')
        df = df.fillna(0)
        y_label = 'growth_rate_tweet'
        y_name = 'tweet count'
    elif avg_rate == "favourite_count":
        df['growth_rate_favourite'] = df[avg_rate].pct_change()
        df['growth_rate_favourite'] = (df["growth_rate_favourite"] * 100).round(5)
        df['date'] = df['date'].astype('str')
        df = df.fillna(0)
        y_label = 'growth_rate_favourite'
        y_name = 'favourite count'

    # filter the dataframe to within the selected date range from the sidebar input widgets
    df['date'] = pd.to_datetime(df['date'])
    startDate_select = pd.to_datetime(startDate_select)
    endDate_select = pd.to_datetime(endDate_select)
    mask = (df['date'] >= startDate_select) & (df['date'] <= endDate_select)
    df = df.loc[mask]
    df['date'] = df['date'].astype('str')

    # calculate average growth rate throughout the years
    average_GR = math.pow((df.iloc[-1][avg_rate] / df.iloc[0][avg_rate]), 1 / len(df)) - 1
    average_GR = round(average_GR * 100, 5)
    # create average_GR into array
    df['average_GR'] = average_GR
    st.write(f"The average of daily growth for {y_name} for the last {len(df)} days: {average_GR}")

    # Altair visualization
    line1 = alt.Chart(df).mark_line(color='royalblue', point=True).encode(
        x='date',
        y=y_label,
    ).properties(
        title=f"{screen_name} Average Growth Rate for {avg_rate}"
    )

    line2 = alt.Chart(df).mark_line(stroke='red',strokeDash=[6,6]).encode(
        x='date',
        y="average_GR"
    )

    # Create a selection that chooses the nearest point & selects based on x-value
    nearest = alt.selection(type='single', nearest=True, on='mouseover',
                            fields=['date'], empty='none')

    # Transparent selectors across the chart. This is what tells us
    # the x-value of the cursor
    selectors = alt.Chart(df).mark_point().encode(
        x='date',
        opacity=alt.value(0),
    ).add_selection(
        nearest
    )

    # Draw points on the line, and highlight based on selection
    points = line1.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    # Draw text labels near the points, and highlight based on selection
    text = line1.mark_text(align='left', dx=5, dy=-5).encode(
        text=alt.condition(nearest, y_label, alt.value(' '))
    )

    # Draw a rule at the location of the selection
    rules = alt.Chart(df).mark_rule(color='gray').encode(
        x='date',
    ).transform_filter(
        nearest
    )

    layer = alt.layer(line1, line2, selectors, points, rules, text).configure_view(
        stroke='transparent'
    ).configure_axis(
        grid=False
    )
    return st.altair_chart(layer, use_container_width=True)

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