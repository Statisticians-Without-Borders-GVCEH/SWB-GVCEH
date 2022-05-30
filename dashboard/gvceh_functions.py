# dashboard functions
from datetime import date, datetime, timedelta, time
import pandas as pd
import numpy as np

def get_seed():
	''' Input the influencer file and add a boolean influencer column to the dataframes.
	Specify the data source in src.'''

	reddit_df = pd.read_csv('./data/demo/reddit_antiwork.csv', 
		parse_dates=['timestamp'], dtype={'created': object, 'score': float})

	twitter_df = pd.read_csv('./data/demo/GVCEH-2022-04-11-tweet-raw-sentiment.csv',
    	parse_dates=['created_at'], dtype={'tweet_id': object})

	# next two lines should be part of post scrape clean-up
	influencer_list = list(pd.read_csv('./dashboard/influencers.csv')['handle'])

	twitter_df['influencer_flag'] = twitter_df['username'].apply(lambda x: 1 if x in influencer_list else 0)

	return twitter_df, reddit_df


def get_data():
    ''' Loading the twitter and reddit datasets and generating a dictionary of dataframes.'''

    twitter_df, reddit_df = get_seed()

    # reddit_df = pd.read_csv('./data/demo/reddit_antiwork.csv',
    #  parse_dates=['timestamp'], dtype={'created': object, 'score': float})

    # twitter_df = pd.read_csv('./data/demo/GVCEH-2022-04-11-tweet-raw-sentiment.csv', 
    # 	parse_dates=['created_at'], dtype={'tweet_id': object})

    return {'Twitter': twitter_df, 'Reddit': reddit_df}


def tooltips():
    ''' A dictionary of tooltips.'''
    readme = {}
    readme['saanich'] = 'Would you like to see an analysis for Twitter or Reddit?'
    readme[
        'langford'] = 'Would you like to see a prior period comparison? This depends on the date range selected i.e. a prior period comparison for 4/10/22 - 4/16/22 would be 4/3/22 - 4/9/22.'

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

    current = df.loc[(df.created_at >= datetime.combine(start, time())) &
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

    by_category = cagg.join(pagg).reset_index()
    by_category.columns = ['Sentiment', 'Current', 'Prior']

    return by_category

# def weighted_agg_sentiments_by_category(cdf, pdf, in_wt):
# 	''' Adding weights separating influencer and non-influencer tweets.'''

# 	cagg = pd.DataFrame(cdf.groupby(['influencer_flag'], as_index=False)['sentiment'].value_counts())
# 	cagg.columns = ['influencer_flag', 'Sentiment', 'cur']

# 	pagg = pd.DataFrame(pdf.groupby(['influencer_flag'], as_index=False)['sentiment'].value_counts())
# 	pagg.columns = ['influencer_flag', 'Sentiment', 'pre']

# 	cagg['cur_scores'] = cagg.apply(lambda x: in_wt * x.cur if x.influencer_flag == True else (1 - in_wt) * x.cur, axis=1)
# 	cagg_by_category =  pd.DataFrame(cagg.groupby(['Sentiment'])['cur_scores'].sum())

# 	pagg['pre_scores'] = pagg.apply(lambda x: in_wt * x.pre if x.influencer_flag == True else (1 - in_wt) * x.pre, axis=1)

# 	by_category =  cagg.merge(pagg, how='left').reset_index(drop=True)


# 	return by_category

def top_influencers(cdf):

	current_influencers = pd.DataFrame(cdf.groupby(['username']).agg({'tweet_id':'count', 'reply_count':'sum', 
		'retweet_count':'sum', 'like_count':'sum', 'influencer_flag':'min', 'num_followers':'max'}).reset_index())

	current_influencers['score'] = current_influencers.apply(lambda x: x.tweet_id * 0.1 + 
		(x.reply_count + x.retweet_count) * 0.25 + x.like_count * 0.05 + 
		x.influencer_flag * 0.45 + np.log(x.num_followers) * 0.15, axis=1)

	current_influencers = current_influencers.sort_values(by=['score'], ascending=False).reset_index(drop=True)
	# current_influencers.columns = ['username', 'Number of Tweets']

	# cnum = pd.DataFrame(current_df.groupby(['username']).max()['num_followers']).reset_index()
	# current_influencers = current_influencers.merge(cnum, left_on='username',
	# 	right_on='username', how='left')
	# current_influencers.columns = ['Username', 'Number of Tweets', 'Number of Followers']

	# st.table(current_influencers.iloc[0:5])
	# fig_3 = px.bar(current_influencers.iloc[0:5], x='Username', y='Number of Tweets', color_discrete_sequence=['#000080'])
	# st.plotly_chart(fig_3)

    # display tweets by top influencer ka option do - button
    # number of tweets in current+previous period by day or, so far ka just one chart

	return current_influencers


def get_appendix_a_locations():
    return(pd.read_csv('./data/appendices/aa.csv'))

def get_lat_long(left_df):
    right_df = pd.read_csv('./data/demo/Geolocation_Mapping - Sheet1.csv')
    return left_df.merge(right_df, left_on='search_neighbourhood',
                         right_on='Appendix A Location', how='inner')

def get_locations(agg_option):
    df = pd.read_csv('./data/appendices/aa.csv')
    return df.loc[df["Category"] == agg_option, "Location"].tolist()

# def agg_tweets_by_users(cdf, pdf):
# 	''' Aggregating number of tweets by username.'''

# 	cagg = pd.DataFrame(cdf['name'].value_counts(sort=True))

# 	pagg = pd.DataFrame(pdf['name'].value_counts(sort=True))
# 	pagg.columns = ['Prior']

# 	influencers = cagg.join(pagg).reset_index
# 	influencers.columns['Number of Tweets', 'Current', '']
