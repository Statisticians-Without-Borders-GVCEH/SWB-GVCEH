import datetime
import itertools
import os
import requests 

import tweepy as tw
import pandas as pd 

from pprint import pprint
from dotenv import load_dotenv

load_dotenv() # imprt out enviroment variables
 
API_KEY = os.environ.get("API_KEY") # consumer
API_SECRET_KEY = os.environ.get("API_SECRET_KEY") # consumer
BEARER_TOKEN = os.environ.get("BEARER_TOKEN")

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")


### setting up the config
MAX_TWEETS = 100


client = tw.Client(bearer_token=BEARER_TOKEN)

#url = "curl -X GET -H "Authorization: Bearer <BEARER TOKEN>" "https://api.twitter.com/2/tweets/20""

# https://datascienceparichay.com/article/python-get-data-from-twitter-api-v2/
# tweepy / api v2 info

def run_search(neighbourhoods, keywords):

    """
        Runs a twitter search based on these keywords
        Returns list of dict of all data found
    """

    ### generate the search string with spaces
    search_string = " ".join((neighbourhoods, keywords))

    return_data = []

    search_query = f"{search_string} lang:en -is:retweet"

    ### time limits
    # TODO: With elevated account
    #start_time = "2021-07-01T00:00:00Z"
    #end_time = "2022-01-01T00:00:00Z"

    # get tweets
    ### limits us last 7 days, need elevated account for longer than that
    tweets = client.search_recent_tweets(
        query=search_query,
        #start_time=start_time,
        #end_time=end_time,
        tweet_fields = ["context_annotations", "public_metrics", "created_at", "text", "source", "geo"],
        user_fields = ["name", "username", "location", "verified", "description", "public_metrics"],
        max_results = MAX_TWEETS,
        place_fields=['country', 'geo', 'name', 'place_type'],
        expansions=['author_id', 'geo.place_id']
    )

    ### not yielding anything? exit early
    if not tweets.data: return []

    ### generate our place information
    if 'places' in tweets.includes.keys():
        place_info = {
            place.id: {
                'bbox': place.geo['bbox'], #geoJSON, min long, min lat, max long, max lat
                'full_name': place.full_name,
                # place.name
                # place.place_type
                # place.full_name
                # place.country
            } for place in tweets.includes['places']
        } 

    for tweet, user in zip(tweets.data, tweets.includes['users']):

        newtweet = {}

        #original text
        newtweet['text'] = tweet.text

        ### scrape time
        newtweet['scrape_time'] = str(datetime.datetime.now())
        
        ### unique ID
        newtweet['tweet_id'] = tweet.id

        # post time
        newtweet['created_at'] = str(tweet.created_at)

        # reply count
        newtweet['reply_count'] = tweet.public_metrics['reply_count']
        # number of quote tweets
        newtweet['quote_count'] = tweet.public_metrics['quote_count']
        # number of likes
        newtweet['like_count'] = tweet.public_metrics['like_count']
        # number of RTs
        newtweet['retweet_count'] = tweet.public_metrics['retweet_count']

        ### geo data (where available)
        newtweet['geo_full_name'] = None
        newtweet['geo_id'] = None
        newtweet['geo_bbox'] = None

        if tweet.geo:          
            newtweet['geo_id'] = tweet.geo['place_id']
            newtweet['geo_full_name'] = place_info[tweet.geo['place_id']]['full_name']
            newtweet['geo_bbox'] = place_info[tweet.geo['place_id']]['bbox']

        ### cordinate data - where available
        ### TODO: validate this work with data with coordinates
        if tweet.geo:
            newtweet['tweet_coordinate'] = tweet.geo.get('coordinates', '')
        else:
            newtweet['tweet_coordinate'] = ''

        # poster
        newtweet['username'] = user.username

        # number of followers
        newtweet['num_followers'] = user.public_metrics['followers_count']

        ### so we know how it was found
        newtweet['search_keywords'] = search_string

        ### more meta data
        newtweet['search_neighbourhood'] = neighbourhoods

        return_data.append(newtweet)

    return return_data

def search_by_neighbourhood_keyword_products():

    ### dummy neighbourhoods
    neighbourhoods = ['Victoria', 'Greater Victoria', 'YYJ', 'GVCEH', 'Topaz Park', 'Beacon Hill Park', 'Pandora', 'Oaklands', 'Fairfield']

    ### dummy keywords
    keywords = ['Homeless', 'Homelessness', 'Encampment', 'Poverty', 'Crime', 'Shelter', 'Tent', 'Overdose']

    data = []

    ### run each product
    for n,k in list(itertools.product(neighbourhoods, keywords)):
        
        # run the search
        data += run_search(neighbourhoods=n, keywords=k)

    ### create pandas df of all data
    df = pd.DataFrame(data)

    ### remove duplicates

    ### write to csv
    filename = f"data/GVCEH-{str(datetime.date.today())}-tweet-raw.csv"
    df.to_csv(filename, encoding='utf-8')

    print(df.head(10))
    print(df.shape)


def main():
    search_by_neighbourhood_keyword_products()
    #search_by_crd_keyword_products()
    #search_by_influencer_keyword_products()
    #search_by_geolocation()

if __name__ == "__main__":
    main()