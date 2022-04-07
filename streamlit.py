import streamlit as st
import pandas as pd
import datetime

# DEFINITIONS
def load_data(DATA_URL): #TODO: Need to confirm what type of data file we're going to be connecting to
    data = pd.read_csv(DATA_URL)
    return data

# containers = horizontal
header = st.container()
dataset = st.container()
features = st.container()
modelTraining = st.container()

my_data = load_data('/Users/sheilaflood/PycharmProjects/Streamlit/data/GVCEH_Test_Data - Sheet1.csv')
max_date_time_obj = datetime.datetime.strptime(my_data['Date Posted'].max(), '%m/%d/%y') # May need to update if input format changes
min_date_time_obj = datetime.datetime.strptime(my_data['Date Posted'].min(), '%m/%d/%y') # May need to update if input format changes

# SIDEBAR - Input Parameters
st.sidebar.title("Visualization Selector")

# TODO: Confirm what date range values we want to use
start_date = st.sidebar.date_input("Start Date:", min_date_time_obj)
end_date = st.sidebar.date_input("End Date:", max_date_time_obj)
# st.sidebar.write('Date Range Selected:', start_date, "-", end_date)

#get the state selected in the selectbox
selected_options = st.sidebar.multiselect('Select one or more options:',
                                          my_data['Source'].unique(),
                                          default = my_data['Source'].unique()
                                          )

#get the state selected in the selectbox
# my_data_selected = my_data[(my_data['Source'] == select)] #TODO: Add dynamic date filter
my_data_selected = my_data[my_data['Source'].isin(selected_options)]
# & (my_data['Date Posted'] >= start_date)

with header:
    st.title('GVCEH Sentiment Analysis App')
    st.text('This app extracts text from online sources and analyzes trends using NLP and \n'
            'machine learning. It is designed for the Greater Victoria Coalition \n'
            'to End Homelessness.')

with dataset:
    st.header('GVCEH Test Dataset')

    st.write(my_data_selected.head())

    st.subheader('Data Distributions')
    col_1, col_2 = st.columns(2)
    sentiment_dist = pd.DataFrame(my_data_selected['Sentiment'].value_counts())
    col_1.bar_chart(sentiment_dist)

    data_source_dist = pd.DataFrame(my_data_selected['Source'].value_counts())
    col_2.bar_chart(data_source_dist)

    st.subheader('Top Influencers')
    st.text('Section for top influencers...')

    st.subheader('Geolocations')
    st.map(my_data_selected[["Latitude", "Longitude"]])

with features:
    st.header('The features I created')
    st.markdown('* **first feature** I created this first feature because of thiss..')
    st.markdown('* **second feature** I created this first feature because of thiss..')
    st.markdown('* **third feature** I created this first feature because of thiss..')


