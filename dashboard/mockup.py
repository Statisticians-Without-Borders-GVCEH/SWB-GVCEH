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

# import sharepoint_conn as sharep

# testing sharepoint_conn file
# test_df = sharep.get_data_sharepoint()
# print(test_df.head())

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

	st.sidebar.header('1. Data')
	option = st.sidebar.selectbox('Select a twitter source',
		('Twitter', 'Reddit'),
		key='saanich', help=readme['saanich'])


	st.sidebar.header('2. Date Range')
	scol1, scol2 = st.sidebar.columns(2)

	start_date = scol1.date_input(
	            "Start Date",
	            date(2022, 4, 8),
	            # min_value=datetime.strptime("2015-02-16", "%Y-%m-%d"),
	            max_value=datetime.now(),
	        )

	end_date = scol2.date_input(
	            "End Date",
	            date(2022, 4, 11),
	            # min_value=datetime.strptime("2015-02-24", "%Y-%m-%d"),
	            max_value=datetime.now(),
	        )

	priorperiod_flag = st.sidebar.checkbox(
	        "Prior period comparison", value=False, help=readme['langford']
	    )

	st.sidebar.header('3. Locations')

	appendix_a = gvceh.get_appendix_a_locations()
	appendix_a_categories = appendix_a["Category"].unique()
	list2 = appendix_a_categories.tolist()
	list1 = ["Capital Region District (All)"]
	agg_levels = list1 + list2



	locations_selected = []
	agg_option = st.sidebar.selectbox('Select an aggregation level:', agg_levels)
	location_option = gvceh.get_locations(agg_option)
	if location_option:
		locations_selected = st.sidebar.multiselect('Select specific location(s):', location_option,
													default=location_option)

# define variables based on user options
use_df = dsource_dict[option]
current_df, prior_df = gvceh.get_frames(start_date, end_date, use_df)
sentiments_by_category = gvceh.agg_sentiments_by_category(current_df, prior_df)
image = Image.open('./dashboard/branding.png')

# wt_try = gvceh.weighted_agg_sentiments_by_category(current_df, prior_df, 0.7)


with header:

	st.image(image)

	st.title('Homelessness in Greater Victoria')
	st.markdown('''This dashboard gives a sense of the sentiment around homelessness in the Greater Victoria area.''')

	st.write(current_df.head())

	st.download_button(
     label="Download twitter as CSV",
     data=use_df.to_csv().encode('utf-8'),
     file_name='twitter.csv')

	# st.write(wt_try)
	st.subheader('Tweets Per Day')

	tweets_per_day = use_df.groupby([use_df['created_at'].dt.date]).tweet_id.nunique()

	fig_0 = px.line(tweets_per_day, x=tweets_per_day.index, y="tweet_id",
		labels={"tweet_id":"Number of Tweets", "created_at":"Date"})
	fig_0.update_traces(line_color='#BF4C41')
	st.plotly_chart(fig_0)

with aggregations:

	# @st.cache
	if start_date > end_date:
	    st.sidebar.error('Error: End date must be on or after the start date.')
	else:
		st.header(option)

		# 1. Viewing a random sample of tweets for sentiment categories
		st.subheader('Sample of Tweets' if option == 'Twitter' else 'Sample of Posts')
		choice = st.selectbox('Choose a sentiment', 
			['Negative', 'Neutral', 'Positive'])
		st.table((current_df.loc[current_df.sentiment == choice].sample(n=5))[['tweet_id', 'username', 'text']])

		# 2. Sentiment Scores Aggregated by Category, with prior period comparison
		st.subheader('Sentiment Scores')
		if priorperiod_flag:
			prior_start_date, prior_end_date = gvceh.get_prior_period(start_date, end_date)
			st.write('Prior period is from', prior_start_date, 'to', prior_end_date)
			fig_1 = px.bar(sentiments_by_category, x='Sentiment', y=['Current', 'Prior'],
				barmode='group', color_discrete_sequence=['#000080', '#8c9e5e']*3)
			st.plotly_chart(fig_1)
		else:
			fig_2 = px.bar(sentiments_by_category, x='Sentiment', y='Current', color_discrete_sequence=['#000080']*3)
			st.plotly_chart(fig_2)

		# 3. Top Influencers
		st.subheader('Top Influencers')
		
		display_tweets = st.checkbox('Display tweets by top influencers.')

		current_influencers = gvceh.top_influencers(current_df)
		# st.table(current_influencers)
		if display_tweets:
			st.table(current_df.loc[current_df['username'].isin(current_influencers.iloc[0:5]['username'])][['username','text']])

		


		# current_influencers = pd.DataFrame(current_df['username'].value_counts(sort=True).reset_index())
		# st.write(current_influencers)
		# current_influencers.columns = ['username', 'Number of Tweets']

		# cnum = pd.DataFrame(current_df.groupby(['username']).max()['num_followers']).reset_index()
		# current_influencers = current_influencers.merge(cnum, left_on='username',
		# 	right_on='username', how='left')
		# current_influencers.columns = ['Username', 'Number of Tweets', 'Number of Followers']

		# st.table(current_influencers.iloc[0:5])
		fig_3 = px.bar(current_influencers.iloc[0:5], x='username', y='score', color_discrete_sequence=['#000080'])
		st.plotly_chart(fig_3)

		# 4. Geolocations
		st.subheader('Locations')
		st.write('Sentiment by topic location')

		if locations_selected:
			current_df = current_df[current_df["search_neighbourhood"].isin(locations_selected)]
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


		if (len(locations_selected) > 0 or agg_option == 'Capital Region District (All)'):
			# Need more twitter to determine how useful this will be
			conditions = [
				(current_df['sentiment'] == "Neutral"),
				(current_df['sentiment'] == "Negative"),
				(current_df['sentiment'] == "Positive")
			]
			values = [0, current_df["score"] * -1, current_df["score"]]
			current_df["polarity"] = np.select(conditions, values)

			j = current_df[["search_neighbourhood", "polarity", "created_at"]]
			j['created_at'] = j['created_at'].dt.date
			wide_form = j.pivot_table(index='created_at',
									  columns='search_neighbourhood',
									  values='polarity',
									  aggfunc='mean',
									  fill_value=0)

			wide_form = wide_form.reset_index()
			long_form = wide_form.melt('created_at', var_name='search_neighbourhood', value_name='avg_score')
			line_chart = alt.Chart(long_form, title="Average Sentiment Scores by Date").mark_line().encode(
				x='yearmonthdate(created_at)',
				y='avg_score:Q',
				tooltip='search_neighbourhood',
				color='search_neighbourhood:N'
			).interactive()
			st.altair_chart(line_chart, use_container_width=True)


		# 	real_data = gvceh.get_lat_long(k)
		# 	st.pydeck_chart(pdk.Deck(
		# 		map_style='mapbox://styles/mapbox/light-v9',
		# 		initial_view_state=pdk.ViewState(
		# 			latitude=48.45,
		# 			longitude=-123.37,
		# 			zoom=11,
		# 			pitch=50,
		# 			tooltip=True,
		# 		),
		# 		tooltip={
		# 			'html': "<b>Number of Tweets:</b> {elevationValue}",
		# 			'style': {
		# 				'color': 'white'
		# 			}
		# 		},
		# 		layers=[
		# 			pdk.Layer(
		# 				'HexagonLayer',
		# 				twitter=real_data,
		# 				get_position='[Longitude, Latitude]',
		# 				auto_highlight=True,
		# 				elevation_scale=4,
		# 				radius=200,
		# 				pickable=True,
		# 				elevation_range=[10, 100],
		# 				get_fill_color=[69, 162, 128, 255],
		# 				extruded=True,
		# 				coverage=1,
		# 			),
		# 		],
		# 	))













