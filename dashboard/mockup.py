# run as streamlit run ./dashboard/mockup.py from the github repo parent dir
import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta, time
import plotly.express as px
import pydeck as pdk
import altair as alt
import numpy as np
import gvceh_functions as gvceh
from PIL import Image

# set page layout
st.set_page_config(layout="wide")

# init streamlit containers
header = st.container()
aggregations = st.container()
sidebar = st.container()


# CSS to inject contained in a string
hide_table_row_index = """
            <style>
            tbody th {display:none}
            .blank {display:none}
            </style>
            """

# Inject CSS with Markdown
st.markdown(hide_table_row_index, unsafe_allow_html=True)

# import twitter
dsource_dict = gvceh.get_data() # replace with get_seed
inf = gvceh.get_seed() # remove

# import the help dictionary
readme = gvceh.tooltips()


with sidebar:
	# data source - twitter or reddit
	# st.sidebar.header('1. Data')
	# option = st.sidebar.selectbox('Select a data source',
	# 	('Twitter', 'Reddit'),
	# 	key='saanich',
	# 	help=readme['saanich'])
	option = 'Twitter'
	use_df = dsource_dict[option]

	st.sidebar.header('1. Date Range')
	scol1, scol2 = st.sidebar.columns(2)

	start_date = scol1.date_input(
			"Start Date",
			value=use_df['created_at'].min().date(),
			max_value=datetime.now(),
		)

	end_date = scol2.date_input(
			"End Date",
			value=use_df['created_at'].max().date(),
			max_value=datetime.now(),
		)

	if start_date > end_date: # TODO: make so error msg only shows on sidebar; not main page.
	    st.sidebar.error('Error: End date must be on or after the start date.')

	priorperiod_flag = st.sidebar.checkbox(
	        "Prior period comparison", value=False, help=readme['langford']
	    )
	
	if priorperiod_flag:
		prior_start_date, prior_end_date = gvceh.get_prior_period(start_date, end_date)
		st.sidebar.write('Prior period is from', prior_start_date, 'to', prior_end_date)
		

	st.sidebar.header('2. Locations')

	appendix_a = gvceh.get_appendix_a_locations()
	appendix_a_categories = appendix_a["Category"].unique()
	list2 = appendix_a_categories.tolist()
	list1 = ["Capital Region District (All)"]
	agg_levels = list1 + list2

	locations_selected = []
	agg_option = st.sidebar.selectbox('Select an aggregation level:', agg_levels)
	location_option = gvceh.get_locations(appendix_a, agg_option)
	if location_option:
		locations_selected = st.sidebar.multiselect('Select specific location(s):', location_option,
													default=location_option)

	st.sidebar.header('3. Display Top Influencer Tweets')
	displaytweets_flag = st.sidebar.checkbox('Display tweets by top influencers', value=False)


	# define variables based on user options
	current_df, prior_df = gvceh.get_frames(start_date, end_date, use_df)
	sentiments_by_category = gvceh.agg_sentiments_by_category(current_df, prior_df)
	image = Image.open('./dashboard/branding.png')


	# additions to sidebar after user input
	st.sidebar.header('4. Download Data')
	st.sidebar.download_button(
		label="Download data as CSV",
		data=use_df.to_csv().encode('utf-8'),
		file_name='twitter.csv'
	)


with header:

	a1, a2 = st.columns([2, 1])
	a1.title('Homelessness in Greater Victoria')
	a1.markdown('''This dashboard gives a sense of the sentiment around homelessness in the Greater Victoria area. 
	Data is collected from Twitter daily and stored in GitHub.''')

	### get a better image after fixing the rest of the layout
	a2.image(image)

	# 1. Graph of tweets per day historically
	st.subheader('Tweets Per Day')
	tweets_per_day = current_df.groupby([current_df['created_at'].dt.date]).tweet_id.nunique()

	st.download_button(
		label="Download results as CSV",
		data=tweets_per_day.to_csv().encode('utf-8'),
		file_name='tweets_per_day.csv')

	fig_0 = px.line(tweets_per_day, x=tweets_per_day.index, y="tweet_id",
		labels={"tweet_id":"Number of Tweets", "created_at":"Date"})
	fig_0.update_traces(line_color='#BF4C41')
	st.plotly_chart(fig_0, use_container_width=True)

	
	# whitespace
	n = 0
	while n < 4:
		a1.write('')
		n = n + 1

	a3, a4 = st.columns(2)

	# 2. Top Influencers
	a3.subheader('Top Influencers')

	current_influencers = gvceh.top_influencers(current_df)
	if displaytweets_flag:
		a3.table(current_df.loc[current_df['username'].isin(current_influencers.iloc[0:5]['username'])][
					 ['username', 'text']])

	fig_3 = px.bar(current_influencers.iloc[0:5], x='username', y='score', color_discrete_sequence=['#000080'])
	a3.plotly_chart(fig_3)

	# 3. Sentiment Scores Aggregated by Category, with prior period comparison
	a4.subheader('Sentiment Scores')
	if priorperiod_flag:
		fig_1 = px.bar(sentiments_by_category, x='Sentiment', y=['Current', 'Prior'],
						   barmode='group', color_discrete_sequence=['#000080', '#8c9e5e'] * 3)
		a4.plotly_chart(fig_1)
	else:
		fig_2 = px.bar(sentiments_by_category, x='Sentiment', y='Current', color_discrete_sequence=['#000080'] * 3)
		a4.plotly_chart(fig_2)


	# 4. Viewing a random sample of tweets for sentiment categories
	st.subheader('Sample of Tweets' if option == 'Twitter' else 'Sample of Posts')
	choice = st.selectbox('Choose a sentiment', ['Negative', 'Neutral', 'Positive'])
	st.table((current_df.loc[current_df.sentiment == choice].sample(n=5))[['username', 'text', 'sentiment', 'keywords', 'search_neighbourhood']])


	# 5. Geolocations
	st.subheader('Locations')

	if locations_selected:
		current_df = current_df[current_df["search_neighbourhood"].isin(locations_selected)]
		if len(current_df) == 0:
			st.write("No data for the selected aggregation level.")
		else:
			k = current_df[["search_neighbourhood", "sentiment"]]
			st.write(k.pivot_table(index='search_neighbourhood',
									   columns='sentiment',
									   aggfunc=len,
									   fill_value=0))

	elif agg_option == 'Capital Region District (All)':
		k = current_df[["search_neighbourhood", "sentiment"]]
		k_pivot = k.pivot_table(index='search_neighbourhood',
									columns='sentiment',
									aggfunc=len,
									fill_value=0)
		st.write(k_pivot)
	else:
		st.sidebar.error("No options selected. Please select at least one location.")

	# TODO: this is throwing an error... commenting out for demo
	# st.download_button(
	# 	label="Download results as CSV",
	# 	data=k_pivot.to_csv().encode('utf-8'),
	# 	file_name='geolocations.csv')

















