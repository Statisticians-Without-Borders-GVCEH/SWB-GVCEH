# dashboard functions
from datetime import date, datetime, timedelta, time
import pandas as pd
import numpy as np
import os


def get_seed():
    ''' Input the influencer file and add a boolean influencer column to the dataframes.
    Specify the twitter source in src.'''

    # reddit_df = pd.read_csv('./data/processed/reddit_antiwork.csv',
    # 	parse_dates=['timestamp'], dtype={'created': object, 'score': float})

    # twitter_df = pd.read_csv('./data/all-raw-merged-2022-06-22_DEMO.csv',
    #     parse_dates=['created_at'], dtype={'tweet_id': object})

    twitter_df = pd.DataFrame([])
    for subdir, dirs, files in os.walk('./data/processed/twitter/github_actions/'):
        for file in files:
            file_path = os.path.join(subdir, file)
            if file_path[-4:] == '.csv':
                # print(file_path)
                df = pd.read_csv(
                    file_path,
                    parse_dates=['created_at'],
                    dtype={'tweet_id': object},
                    usecols=["text", "scrape_time", "tweet_id", "created_at", "reply_count", "quote_count",
                             "like_count", "retweet_count", "geo_full_name", "geo_id", "username", "num_followers",
                             "search_keywords", "search_neighbourhood", "sentiment", "score"]
                )
                twitter_df = pd.concat([df, twitter_df])


    # next two lines should be part of post scrape clean-up
    influencer_list = list(pd.read_csv('./dashboard/influencers.csv')['handle'])
    twitter_df['influencer_flag'] = twitter_df['username'].apply(lambda x: 1 if x in influencer_list else 0)

    return twitter_df
    # return twitter_df, reddit_df


def get_data():
    ''' Loading the twitter and reddit datasets and generating a dictionary of dataframes.'''

    # twitter_df, reddit_df = get_seed()
    twitter_df = get_seed()

    # reddit_df = pd.read_csv('./twitter/demo/reddit_antiwork.csv',
    #  parse_dates=['timestamp'], dtype={'created': object, 'score': float})

    # twitter_df = pd.read_csv('./twitter/demo/GVCEH-2022-04-11-tweet-raw-sentiment.csv',
    # 	parse_dates=['created_at'], dtype={'tweet_id': object})

    return {'Twitter': twitter_df}
    # return {'Twitter': twitter_df, 'Reddit': reddit_df}


def tooltips():
    ''' A dictionary of tooltips.'''
    readme = {}
    readme['data_source'] = 'Would you like to see an analysis for Twitter or Reddit?'
    readme['prior_period'] = 'A prior period comparison enables comparison of results for this period against the previous period. e.g. the prior period for 4/10/22 - 4/16/22 would be 4/3/22 - 4/9/22.'
    readme['top_influencers'] = 'The top influencers for a time period are calculated using a weighted measure of number of tweets, reply and retweet count, like count, number of followers and an influencer flag based on the appendix.'
    
    return readme


def get_prior_period(start, end):
    ''' Get the start and end dates for the prior period.'''

    timeperiod = end - start

    prev_end = start - timedelta(days=1)
    prev_start = prev_end - timeperiod

    return prev_start, prev_end

# test: 01_test_prior_period_calc

def get_frames(start, end, df):
    ''' Get a two subsets of a dataframe based on start and end dates,
	a current and prior period dataframe.'''

    prev_start, prev_end = get_prior_period(start, end)

    df['created_at'] = pd.to_datetime(df.created_at).dt.tz_localize(None)

    current = df.loc[(df.created_at >= datetime.combine(start, time())) &
                     (df.created_at <= datetime.combine(end, time()))]

    prior = df.loc[(df.created_at >= datetime.combine(prev_start, time())) &
                   (df.created_at <= datetime.combine(prev_end, time()))]

    return current, prior


def agg_sentiments_by_category(cdf, pdf):
    ''' Aggregating number of sentiments by category and
	generating a single dataframe with current and prior period aggregations.'''

    cagg = pd.DataFrame(cdf['sentiment'].value_counts())

    pagg = pd.DataFrame(pdf['sentiment'].value_counts())
    pagg.columns = ['Prior']

    by_category = cagg.join(pagg).reset_index()
    by_category.columns = ['Sentiment', 'Current', 'Prior']

    by_category.sort_values(by=['Sentiment'], ascending=False, inplace=True)

    return by_category

# test: 02_test_sentiment_agg


def top_influencers(cdf):

    current_influencers = pd.DataFrame(cdf.groupby(['username']).agg({'tweet_id':'count', 'reply_count':'sum',
		'retweet_count':'sum', 'like_count':'sum', 'influencer_flag':'min', 'num_followers':'max'}).reset_index())

    current_influencers['score'] = current_influencers.apply(lambda x: x.tweet_id * 0.1 +
		(x.reply_count + x.retweet_count) * 0.25 + x.like_count * 0.05 + 
		x.influencer_flag * 0.45 + np.log(x.num_followers) * 0.15, axis=1)

    current_influencers = current_influencers.sort_values(by=['score'], ascending=False).reset_index(drop=True)

    return current_influencers

# test: 03_test_top_influencers


def get_appendix_a_locations():
    df = pd.read_csv('./appendices/aa.csv')
    return(df)

# def get_lat_long(left_df):
#     right_df = pd.read_csv('./twitter/demo/Geolocation_Mapping - Sheet1.csv')
#     return left_df.merge(right_df, left_on='search_neighbourhood',
#                          right_on='Appendix A Location', how='inner')

def get_locations(appendix_df, agg_option):
    return appendix_df.loc[appendix_df["Category"] == agg_option, "Location"].tolist()
