# run as streamlit run ./dashboard/mockup.py from the github repo parent dir
import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta, time
import gvceh_functions as gvceh
import plotly.express as px
import pydeck as pdk
import numpy as np

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

		# 1. Viewing a random sample of tweets for sentiment categories
		st.subheader('Sample of Tweets' if option == 'Twitter' else 'Sample of Posts')
		choice = st.selectbox('Choose a sentiment', 
			['Negative', 'Neutral', 'Positive'])
		st.table((current_df.loc[current_df.sentiment == choice].sample(n=5))[['tweet_id', 'username', 'text']])

		# 2. Demo of the metrics feature
		st.subheader('Metrics Feature')
		st.markdown("This feature is currently based on dummy numbers and is for demonstration purposes only.")
		mcol1, mcol2, mcol3 = st.columns(3)
		mcol1.metric('Positive', 42, 2)
		mcol2.metric('Neutral', 2, 3)
		mcol3.metric('Negative', 4, 5)

		# 3. Sentiment Scores Aggregated by Category, with prior period comparison
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

		# 4. Top Influencers
		st.subheader('Top Influencers')
		
		current_influencers = pd.DataFrame(current_df['username'].value_counts(sort=True).reset_index())
		current_influencers.columns = ['username', 'Number of Tweets']

		cnum = pd.DataFrame(current_df.groupby(['username']).max(['num_followers'])['num_followers']).reset_index()
		current_influencers = current_influencers.merge(cnum, left_on='username',
			right_on='username', how='left')
		current_influencers.columns = ['Username', 'Number of Tweets', 'Number of Followers']

		st.table(current_influencers.iloc[0:5])
		fig_3 = px.bar(current_influencers.iloc[0:5], x='Username', y='Number of Tweets', color_discrete_sequence=['#000080'])
		st.plotly_chart(fig_3)

	
		# 5. Geolocations
		st.subheader('Geolocations')

		# Creating test data until we can use real data
		test_data = pd.DataFrame(
			{'Appendix A Location': ['Central Park', 'Royal Athletic Park', 'Topaz Park', 'Royal Athletic Park',
									 'Topaz Park', 'Central Park', 'Central Park', 'Hollywood Park', 'Stadacona Park'],
			 'Sentiment': ['negative', 'neutral', 'positive', 'negative', 'positive', 'negative', 'neutral',
						   'negative', 'neutral']})
		test_data2 = gvceh.get_lat_long(test_data)

		st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v9',
            initial_view_state=pdk.ViewState(
                latitude=48.45,
                longitude=-123.37,
                zoom=11,
                pitch=50,
                tooltip=True,
            ),
            tooltip={
                'html': "<b>Number of Tweets:</b> {elevationValue}",
                'style': {
                    'color': 'white'
                }
            },
            layers=[
                pdk.Layer(
                    'HexagonLayer',
                    data=test_data2,
                    get_position='[Longitude, Latitude]',
                    auto_highlight=True,
                    elevation_scale=4,
                    radius=200,
                    pickable=True,
                    elevation_range=[10, 100],
                    get_fill_color=[69, 162, 128, 255],
                    extruded=True,
                    coverage=1,
                ),
                # pdk.Layer(
                # 	'ScatterplotLayer',
                # 	data=test_data2,
                # 	get_position='[Longitude, Latitude]',
                # 	get_color='[200, 30, 0, 160]',
                # 	get_radius=200,
                # 	get_fill_color= '[180, 0, 200, 140]', # Set an RGBA value for fill
                # 	pickable = True
                # ),
            ],
        ))











