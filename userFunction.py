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

def emptyLine():
    st.markdown("***")

def getDate(endDate):
    today = endDate  # current date and time
    yesterday = today - datetime.timedelta(days=1)
    date_today = today.strftime("%Y-%m-%d")
    date_yesterday = yesterday.strftime("%Y-%m-%d")
    return date_today, date_yesterday

@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def getprofileImg(screen_name, endDate):
    endDate = endDate.strftime("%Y%m%d")
    f_name = "output/users/{}/user_profile_{}.json".format(screen_name, endDate)
    with open(f_name) as f:
        profile = json.load(f)
        img = (profile['profile_image_url_https'])
    img = img.replace('_normal', '')
    return img

@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def getuserProfile(screen_name, startDate, endDate):
    arr_date = []
    rng = pd.date_range(startDate, endDate, freq='D')
    for i, x in enumerate(rng):
        x = x.strftime("%Y%m%d")
        arr_date.append(x)

    tweet_count = []
    num_followers = []
    num_friends = []
    favourite_count = []
    created_at = []
    for x in arr_date:
        f_name = "output/users/{}/user_profile_{}.json".format(screen_name, x)
        with open(f_name) as f:
            profile = json.load(f)
            num_followers.append(profile['followers_count'])
            num_friends.append(profile['friends_count'])
            tweet_count.append(profile['statuses_count'])
            favourite_count.append(profile['favourites_count'])
            created_at.append(profile['created_at'])

    df = pd.DataFrame({
        'date': rng,
        'created_at': created_at,
        'num_of_tweet': tweet_count,
        'favourite_count': favourite_count,
        'followers_count': num_followers,
        'friends_count': num_friends
    })
    df['date'] = df['date'].astype('str')
    df['created_at'] = df['created_at'].astype('datetime64')
    df['created_at'] = df['created_at'].dt.tz_localize('UTC')
    df['created_at'] = df['created_at'].dt.tz_convert(pytz.timezone('Asia/Kuala_Lumpur'))
    return df

@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def getfollowersProfile(accName, startDate, endDate):
    arr_date = []
    rng = pd.date_range(startDate, endDate, freq='D')
    for i, x in enumerate(rng):
        x = x.strftime("%Y%m%d")
        arr_date.append(x)

    screen_name = []
    followers_count = []
    friends_count = []
    created_at = []
    tweet_count = []
    for x in arr_date:
        f_name = "output/users/{}/followers_{}.json".format(accName, x)
        if Path(f_name).is_file():
            with open(f_name, 'r') as f:
                for line in f:
                    profile = json.loads(line)
                    screen_name.append(profile["screen_name"])
                    friends_count.append(profile['friends_count'])
                    followers_count.append(profile['followers_count'])
                    created_at.append(profile['created_at'])
                    tweet_count.append(profile['statuses_count'])
    df_followers = pd.DataFrame({
        'followers_screen_name': screen_name,
        'created_at': created_at,
        'friends_count': friends_count,
        'followers_count': followers_count,
        'tweet_count': tweet_count
    })
    df_followers['created_at'] = df_followers['created_at'].astype('datetime64')
    df_followers['created_at'] = df_followers['created_at'].dt.tz_localize('UTC')
    df_followers['created_at'] = df_followers['created_at'].dt.tz_convert(pytz.timezone('Asia/Kuala_Lumpur'))
    df_followers.drop_duplicates(subset=['followers_screen_name'], keep='last', inplace=True, ignore_index=True)
    mask = (df_followers['created_at'] >= '2006-1-1')
    df_followers = df_followers.loc[mask]
    df_followers.reset_index(inplace=True, drop=True)
    return df_followers

@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def getfriendsProfile(accName, startDate, endDate):
    arr_date = []
    rng = pd.date_range(startDate, endDate, freq='D')
    for i, x in enumerate(rng):
        x = x.strftime("%Y%m%d")
        arr_date.append(x)

    screen_name = []
    followers_count = []
    friends_count = []
    created_at = []
    tweet_count = []
    for x in arr_date:
        f_name = "output/users/{}/friends_{}.json".format(accName, x)
        if Path(f_name).is_file():
            with open(f_name, 'r') as f:
                for line in f:
                    profile = json.loads(line)
                    screen_name.append(profile["screen_name"])
                    friends_count.append(profile['friends_count'])
                    followers_count.append(profile['followers_count'])
                    created_at.append(profile['created_at'])
                    tweet_count.append(profile['statuses_count'])
    df_friends = pd.DataFrame({
        'friends_screen_name': screen_name,
        'created_at': created_at,
        'friends_count': friends_count,
        'followers_count': followers_count,
        'tweet_count': tweet_count
    })
    df_friends['created_at'] = df_friends['created_at'].astype('datetime64')
    df_friends['created_at'] = df_friends['created_at'].dt.tz_localize('UTC')
    df_friends['created_at'] = df_friends['created_at'].dt.tz_convert(pytz.timezone('Asia/Kuala_Lumpur'))
    df_friends.drop_duplicates(subset=['friends_screen_name'], keep='last', inplace=True, ignore_index=True)
    mask = (df_friends['created_at'] >= '2006-1-1')
    df_friends = df_friends.loc[mask]
    df_friends.reset_index(inplace=True, drop=True)
    return df_friends

@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def getuserTimeline(screen_name, endDate):
    endDate = endDate.strftime("%Y%m%d")
    timeline_file = "output/user_timeline_{}_{}.json".format(screen_name, endDate)
    with open(timeline_file) as f1:
        created_at = []
        retweet_count = []
        favorite_count = []
        tweet_text = []
        hashtags = []
        media_type = []
        user_mention = []
        urls = []
        quote_retweet_status = []
        for line in f1:
            tweet = json.loads(line)
            retweet_count.append(tweet['retweet_count'])
            favorite_count.append(tweet['favorite_count'])
            tweet_text.append(tweet['text'])
            created_at.append(tweet['created_at'])
            # if hashtags included in the tweet or not
            if (len(tweet['entities']['hashtags']) != 0):
                hashtags.append([tweet['entities']['hashtags'][0]["text"]])
            else:
                hashtags.append([])
            # type of media included in the tweet
            if ("extended_entities" in tweet):
                if (tweet['extended_entities']['media'][0].get('type') == "photo"):
                    media_type.append("photo")
                elif (tweet['extended_entities']['media'][0].get('type') == "video"):
                    media_type.append("video")
                elif (tweet['extended_entities']['media'][0].get('type') == "animated_gif"):
                    media_type.append("animated_gif")
            else:
                media_type.append("no_media")
            # is there any user mentioned in the tweet
            if (len(tweet['entities']['user_mentions']) != 0):
                user_mention.append([tweet['entities']['user_mentions'][0]["screen_name"]])
            else:
                user_mention.append([])
            # if there is link included in the tweet
            if (len(tweet['entities']['urls']) != 0):
                urls.append("True")
            else:
                urls.append("False")
            # if the tweet is the quote retweet from other tweet or not
            if (tweet['is_quote_status'] == True):
                quote_retweet_status.append("True")
            else:
                quote_retweet_status.append("False")
    df_timeline = pd.DataFrame({
        'tweet_content':tweet_text,
        'created_at':created_at,
        'retweet_count':retweet_count,
        'favorite_count':favorite_count,
        'hashtags':hashtags,
        'media_type':media_type,
        'user_mention':user_mention,
        'urls':urls,
        'quote_retweet_status':quote_retweet_status
    })
    df_timeline['created_at'] = df_timeline['created_at'].astype('datetime64')
    df_timeline['created_at'] = df_timeline['created_at'].dt.tz_localize('UTC')
    df_timeline['created_at'] = df_timeline['created_at'].dt.tz_convert(pytz.timezone('Asia/Kuala_Lumpur'))
    return df_timeline

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
    df = pd.merge(df1, df2, how='inner', on=['screen_name'])
    df.drop(columns=['created_at_y', 'friends_count_y', 'followers_count_y', 'tweet_count_y'], inplace=True)
    df.rename(columns={
        'created_at_x': 'created_at',
        'friends_count_x': 'friends_count',
        'followers_count_x': 'followers_count',
        'tweet_count_x': 'tweet_count'
    }, inplace=True)
    return df


def getbrand_Mention(screen_name, startDate, endDate):
    arr_date = []
    rng = pd.date_range(startDate, endDate, freq='D')
    for i, x in enumerate(rng):
        x = x.strftime("%Y%m%d")
        arr_date.append(x)

    tweet_text = []
    created_at = []
    retweet_count = []
    favorite_count = []
    for x in arr_date:
        f_name = "output/brand_mentions/brand_mention_{}_{}.json".format(screen_name,x)
        if Path(f_name).is_file():
            with open(f_name) as f:
                for line in f:
                    tweet = json.loads(line)
                    tweet_text.append(tweet['text'])
                    created_at.append(tweet['created_at'])
                    retweet_count.append(tweet['retweet_count'])
                    favorite_count.append(tweet['favorite_count'])
    df = pd.DataFrame({'tweet_text': tweet_text,
                       'created_at': created_at,
                       'retweet_count': retweet_count,
                       'favorite_count': favorite_count
                       })
    df['created_at'] = df['created_at'].astype('datetime64')
    df['created_at'] = df['created_at'].dt.tz_localize('UTC')
    df['created_at'] = df['created_at'].dt.tz_convert(pytz.timezone('Asia/Kuala_Lumpur'))
    df.drop_duplicates(subset=['tweet_text'], keep='last', inplace=True, ignore_index=True)
    df.reset_index(inplace=True, drop=True)
    return df

def getKPI(df, date_today, date_yesterday):
    followers_num_today = df.loc[df['date'] == date_today, 'followers_count'].iloc[0]
    followers_num = int(followers_num_today)
    followers_num_yesterday = df.loc[df['date'] == date_yesterday, 'followers_count'].iloc[0]
    followers_diff = int(followers_num_today) - int(followers_num_yesterday)

    friends_num_today = df.loc[df['date'] == date_today, 'friends_count'].iloc[0]
    friends_num = int(friends_num_today)
    friends_num_yesterday = df.loc[df['date'] == date_yesterday, 'friends_count'].iloc[0]
    friends_diff = int(friends_num_today) - int(friends_num_yesterday)

    tweet_num_today = df.loc[df['date'] == date_today, 'num_of_tweet'].iloc[0]
    tweet_num = int(tweet_num_today)
    tweet_num_yesterday = df.loc[df['date'] == date_yesterday, 'num_of_tweet'].iloc[0]
    tweet_diff = int(tweet_num_today) - int(tweet_num_yesterday)

    fav_num_today = df.loc[df['date'] == date_today, 'favourite_count'].iloc[0]
    fav_num = int(fav_num_today)
    fav_num_yesterday = df.loc[df['date'] == date_yesterday, 'favourite_count'].iloc[0]
    fav_diff = int(fav_num_today) - int(fav_num_yesterday)

    return followers_num, followers_diff, friends_num, friends_diff, tweet_num, tweet_diff, fav_num, fav_diff

def get_topMention(df):
    top_mention = Counter()
    for i, row in df.iterrows():
        top_mention.update(row['user_mention'])
    user_arr = []
    count_arr = []
    for user, count in top_mention.most_common(10):
        user = "@" + user
        user_arr.append(user)
        count_arr.append(count)
    df = pd.DataFrame({
        'user': user_arr,
        'count': count_arr
    })
    return df

def get_topHashtag(df):
    top_hashtag = Counter()
    for i, row in df.iterrows():
        top_hashtag.update(row['hashtags'])
    hashtag_arr = []
    count_arr = []
    for hashtag, count in top_hashtag.most_common(10):
        hashtag = "#" + hashtag
        hashtag_arr.append(hashtag)
        count_arr.append(count)
    df = pd.DataFrame({
        'hashtag': hashtag_arr,
        'count': count_arr
    })
    return df

def get_topFollowerDoC(df_followers):
    df = df_followers.copy()
    df['count'] = df['friends_count'] + df['followers_count']
    df.drop(columns=['created_at','friends_count','followers_count','tweet_count'],inplace=True)
    df.sort_values(by='count', inplace=True, ascending=False)
    df.reset_index(inplace=True, drop=True)
    return df

def get_topFriendDoC(df_friends):
    df = df_friends.copy()
    df['count'] = df['friends_count'] + df['followers_count']
    df.drop(columns=['created_at', 'friends_count', 'followers_count', 'tweet_count'], inplace=True)
    df.sort_values(by='count', inplace=True, ascending=False)
    df.reset_index(inplace=True, drop=True)
    return df

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
        dx=3,  # Nudges text to right so it doesn't appear on top of the bar
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

def growthRate(screen_name, df, avg_rate, startDate_select, endDate_select):
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

def engagement_tweetType(df, days_select):
    df.loc[df['media_type'] == "no_media", 'media_type'] = "text_only"
    df.loc[df['media_type'] == "photo", 'media_type'] = "text_and_photo"
    df.loc[df['media_type'] == "video", 'media_type'] = "text_and_video"
    df.loc[df['media_type'] == "animated_gif", 'media_type'] = "text_and_animated_gif"
    endDate = datetime.datetime.now()
    startDate = endDate - datetime.timedelta(days=days_select)
    df = df.loc[:,['created_at','retweet_count','favorite_count','media_type']]
    df['created_at'] = pd.to_datetime(df.created_at).dt.tz_localize(None)
    mask = (df['created_at'] >= startDate) & (df['created_at'] <= endDate)
    df = df.loc[mask]
    df = df.rename(columns={'media_type': 'tweet_type'})
    df = df.groupby(['tweet_type']).agg(['sum', 'count'])
    df.reset_index(inplace=True)

    df['retweet_average'] = df['retweet_count']['sum'] / df['retweet_count']['count']
    df['favorite_average'] = df['favorite_count']['sum'] / df['favorite_count']['count']
    df.drop(columns = ['retweet_count', 'favorite_count'], axis=1, inplace=True)
    df = df.melt(id_vars='tweet_type').rename(columns=str.title)
    df.drop(columns = ['Variable_1'], axis=1, inplace=True)
    df.rename(columns={'Variable_0': 'Engagement'}, inplace=True)
    df['Value'] = df['Value'].round()

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

def engagement_timeBin(df, days_select):
    endDate = datetime.datetime.now()
    startDate = endDate - datetime.timedelta(days=days_select)

    # define the bins
    # reference: https://www.learnersdictionary.com/qa/parts-of-the-day-early-morning-late-morning-etc
    bins = [0, 5, 12, 17, 21, 24]
    # add custom labels if desired
    labels = ['night_1', 'morning', 'afternoon', 'evening', 'night']

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

def engagement_BrandMention(df_brandMention, days_select):
    endDate = datetime.datetime.now()
    startDate = endDate - datetime.timedelta(days=days_select)
    df = df_brandMention.copy()
    df['created_at'] = pd.to_datetime(df.created_at).dt.tz_localize(None)
    mask = (df['created_at'] >= startDate) & (df['created_at'] <= endDate)
    df = df.loc[mask]
    df.reset_index(inplace=True, drop=True)
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