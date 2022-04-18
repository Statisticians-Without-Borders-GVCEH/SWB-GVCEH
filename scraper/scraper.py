import datetime
import itertools
import os
import requests 
import random
import pickle

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
TESTING = False


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
    search_query = search_query.replace('and', '"and"')

    print("="*40)
    print(f"Searching for... {search_query}")

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

    ### dummy neighbourhoods - Appendix A
    #neighbourhoods = ['Victoria', 'Greater Victoria', 'YYJ', 'GVCEH', 'Topaz Park', 'Beacon Hill Park', 'Pandora', 'Oaklands', 'Fairfield']

    data = pd.read_csv('../data/appendices/aa.csv', index_col=0)

    neighbourhoods = [n.strip() for n in data.Location.tolist()]

    ### searchwords - Appendix C, D and E
    #keywords = ['Homeless', 'Homelessness', 'Encampment', 'Poverty', 'Crime', 'Shelter', 'Tent', 'Overdose']
    data = pd.read_csv('../data/appendices/ac.csv', index_col=0)
    kw1 = [k.strip() for k in data.Organizations.tolist()]

    data = pd.read_csv('../data/appendices/ad.csv', index_col=0)
    kw2 = [k.strip() for k in data.sectors.tolist()]

    data = pd.read_csv('../data/appendices/ae.csv', index_col=0)
    kw3 = [k.strip() for k in data.word.tolist()]

    keywords = kw1 + kw2 + kw3

    #### this is for testing so we dont blow through our entire limit of tweets
    if TESTING:
        neighbourhoods = random.sample(neighbourhoods, 10)
        keywords = random.sample(keywords, 10)

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

def load_keywords():
    """
        Loads our appendices into a dict of lists:
        returns: {
            'ac': [],
            'ad': [],
            'ae': []
        }
    """
    data = pd.read_csv('../data/appendices/ac.csv', index_col=0)
    kw1 = [k.strip().lower() for k in data.Organizations.tolist()]

    data = pd.read_csv('../data/appendices/ad.csv', index_col=0)
    kw2 = [k.strip().lower() for k in data.sectors.tolist()]

    data = pd.read_csv('../data/appendices/ae.csv', index_col=0)
    kw3 = [k.strip().lower() for k in data.word.tolist()]

    return {
        'ac': kw1,
        'ad': kw2,
        'ae': kw3
    }

def gen_query_one(KEYWORDS_DICT):
    """
        Generates a list of queries containing neighbourhood x keyword products
    """

    ### get our neighbourhoods
    data = pd.read_csv('../data/appendices/aa.csv', index_col=0)

    neighbourhoods = [n.strip().lower() for n in data.Location.tolist()]

    ### make one list of keywords
    allkw = sum(KEYWORDS_DICT.values(), [])

    ### chunk it down, we can't exceed 512 character a query
    allkw = [allkw[i::5] for i in range(5)]

    subq = []

    for a in allkw: 
        ### we use OR to help reduce number of queries
        subq.append(" OR ".join(a))

    ### now to make our queries with the neighbourhoods
    query1 = []
    max = 0

    for n in neighbourhoods:
        for kws in subq:
            querytext = f"{n} ({kws}) lang:en -is:retweet"
            #max = len(querytext) if len(querytext) > max else max
            query1.append(querytext)

    #print(max)

    ### returing a list of queries from this product
    return query1

def gen_query_two(KEYWORD_DICT):
    """
        Generate list of CRD identifies x keywords 
    """

    pass

def gen_queries():
    # load keywords
    keywords = load_keywords()

    ### prep keyword union

    # query 1 - neighbourhood keyword products 
    print("Generating Query 1...")
    q1 = gen_query_one(keywords)

    # query 2 - CRD keyword products
    print("Generating Query 2...")
    q2 = gen_query_two(keywords)

    # query 3 - account keyword products
    # query 4

    # no single query more than 512 characters
    # figure out the combining and and or in twitter keywords

    # cache queries
    print("Writing...")
    with open('querylist.pkl', 'wb') as f:
        pickle.dump(q1, f)

def batch_scrape():
    ### manage the pickle json data

    ### probably manage the data file

    ### figure out what attempt at scraping this is?

    ### pull those n queries

    ### pass to scraper

    ### scrape

    ### update scrape info
    pass

if __name__ == "__main__":
    #main()

    ### gen_queries
    gen_queries()

    ### batch scrape
    batch_scrape()