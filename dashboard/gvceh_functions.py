# dashboard functions
from datetime import date, datetime, timedelta, time
import pandas as pd

def get_data():
	''' Loading the twitter and reddit datasets and generating a dictionary of dataframes.'''
	reddit_df = pd.read_csv('./data/demo/reddit_antiwork.csv',
	# reddit_df = pd.read_csv('/Users/sheilaflood/PycharmProjects/SWB-GVCEH/data/demo/reddit_antiwork.csv',
	parse_dates=['timestamp'], dtype={'created':object})

	twitter_df = pd.read_csv('./data/demo/GVCEH-2022-04-11-tweet-raw-sentiment.csv',
	# twitter_df = pd.read_csv('/Users/sheilaflood/PycharmProjects/SWB-GVCEH/data/demo/GVCEH-2022-04-11-tweet-raw-sentiment.csv',
	parse_dates=['created_at'], dtype={'tweet_id':object})

	return {'Twitter': twitter_df, 'Reddit': reddit_df}


def tooltips():
	''' A dictionary of tooltips.'''
	readme = {}
	readme['saanich'] = 'Would you like to see an analysis for Twitter or Reddit?'
	readme['langford'] = 'Would you like to see a prior period comparison? This depends on the date range selected i.e. a prior period comparison for 4/10/22 - 4/16/22 would be 4/3/22 - 4/9/22.'

	return readme

def get_prior_period(start, end):
	''' Get the start and end dates for the prior period.'''

	timeperiod = end - start

	prev_end = start - timedelta(days=1)
	prev_start = prev_end - timeperiod

	return prev_start, prev_end

def get_frames(start, end, df):
	''' Get a two subsets of a dataframe based on start and end dates, 
	a current and prior period dataframe.'''
	
	prev_start, prev_end = get_prior_period(start, end)

	df['created_at'] = pd.to_datetime(df.created_at).dt.tz_localize(None)

	current =  df.loc[(df.created_at >= datetime.combine(start, time())) & 
	(df.created_at <= datetime.combine(end, time()))]

	# current =  df.loc[(df.created_at >= pd.Timestamp(start)) & 
	# (df.created_at <= pd.Timestamp(end))]
	
	prior = df.loc[(df.created_at >= datetime.combine(prev_start, time())) & 
	(df.created_at <= datetime.combine(prev_end, time()))]

	# prior = df.loc[(df.created_at >= pd.Timestamp(prev_start)) & 
	# (df.created_at <= pd.Timestamp(prev_end))]


	return current, prior


def agg_sentiments_by_category(cdf, pdf):
	''' Aggregating number of sentiments by category and 
	generating a single dataframe with current and prior period aggregations.'''

	cagg = pd.DataFrame(cdf['sentiment'].value_counts())

	pagg = pd.DataFrame(pdf['sentiment'].value_counts())
	pagg.columns = ['Prior']

	by_category =  cagg.join(pagg).reset_index()
	by_category.columns = ['Sentiment', 'Current', 'Prior']

	return by_category


def get_lat_long(left_df):
	# right_df = pd.read_csv('/Users/sheilaflood/PycharmProjects/SWB-GVCEH/data/demo/Geolocation_Mapping - Sheet1.csv')
	right_df = pd.read_csv('./data/demo/Geolocation_Mapping - Sheet1.csv')
	return left_df.merge(right_df, on='Appendix A Location', how='left')





