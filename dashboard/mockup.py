# run as streamlit run ./dashboard/mockup.py from the github repo parent dir
import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta, time
import gvceh_functions as gvceh
import plotly.express as px

# init streamlit containers
header = st.container()
aggregations = st.container()
sidebar = st.container()

# import data
dsource_dict = gvceh.get_data()

# import the help dictionary
readme = gvceh.tooltips()


with sidebar:

	st.sidebar.header('1. Data')
	option = st.sidebar.selectbox('Select a data source', 
		('Twitter', 'Reddit'),
		key='saanich', help=readme['saanich'])


	st.sidebar.header('2. Date Range')
	scol1, scol2 = st.sidebar.columns(2)

	start_date = scol1.date_input(
	            "Start Date",
	            date(2020, 2, 16),
	            min_value=datetime.strptime("2015-02-16", "%Y-%m-%d"),
	            max_value=datetime.now(),
	        )

	end_date = scol2.date_input(
	            "End Date",
	            date(2020, 2, 24),
	            min_value=datetime.strptime("2015-02-24", "%Y-%m-%d"),
	            max_value=datetime.now(),
	        )

	priorperiod_flag = st.sidebar.checkbox(
	        "Prior period comparison", value=True, help=readme['langford']
	    )

# define variables based on user options
use_df = dsource_dict[option]
current_df, prior_df = gvceh.get_frames(start_date, end_date, use_df)
sentiments_by_category = gvceh.agg_sentiments_by_category(current_df, prior_df)


with header:

	st.title('Homelessness in Greater Victoria')
	st.markdown('''This dashboard gives a sense of the sentiment around homelessness in the Greater Victoria area.''')

with aggregations:

	# @st.cache
	if start_date > end_date:
	    st.sidebar.error('Error: End date must be on or after the start date.')
	else:
		st.header(option)
		st.write(current_df.head())

		st.subheader('Metrics Feature')
		mcol1, mcol2, mcol3 = st.columns(3)
		mcol1.metric('Positive', 42, 2)
		mcol2.metric('Neutral', 2, 3)
		mcol3.metric('Negative', 4, 5)

		st.subheader('Sentiment Scores')
		fig = px.bar(sentiments_by_category, x='Sentiment', y='Current')
		st.plotly_chart(fig)

		st.subheader('Top Influencers')
		tweets_by_user = pd.DataFrame(current_df['name'].value_counts(sort=True))
		st.write(tweets_by_user.iloc[0:5])
		st.bar_chart(tweets_by_user.iloc[0:5])
