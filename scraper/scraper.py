import datetime
import itertools

import tweepy as tw
import pandas as pd 

from pprint import pprint
 
API_KEY = "" # consumer
API_SECRET_KEY = "" # consumer
BEARER_TOKEN = ""

ACCESS_TOKEN = ""
ACCESS_TOKEN_SECRET = ""


client = tw.Client(bearer_token=BEARER_TOKEN)

#url = "curl -X GET -H "Authorization: Bearer <BEARER TOKEN>" "https://api.twitter.com/2/tweets/20""

# https://datascienceparichay.com/article/python-get-data-from-twitter-api-v2/
# tweepy / api v2 info

def run_search(keywords):

    """
        Runs a twitter search based on these keywords
        Returns list of dict of all data found
    """

    return_data = []

    search_query = f"{keywords} lang:en -is:retweet"

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
        max_results = 25,
        expansions='author_id'
    )

    ### not yielding anything? exit early
    if not tweets.data: return []


    for tweet, user in zip(tweets.data, tweets.includes['users']):
        ### trying to figure out how to get coordinates
        #print(tweet.get('place', {}))
        #print(tweet.get('coordinates', {None, None}))
        #print(user.get('location', {}))

        newtweet = {}

        #print("="*40)

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

        # poster
        newtweet['username'] = user.username

        # number of followers
        newtweet['num_followers'] = user.public_metrics['followers_count']

        ### so we know how it was found
        newtweet['keywords'] = keywords

        return_data.append(newtweet)

    return return_data

def search_by_neighbourhood_keyword_products():
    ### dummy neighbourhoods
    neighbourhoods = ['Victoria', 'Greater Victoria', 'YYJ', 'GVCEH', 'Topaz Park', 'Beacon Hill Park', 'Pandora', 'Oaklands', 'Fairfield']
    ### dummy keywords
    keywords = ['Homeless', 'Homelessness', 'Encampment', 'Poverty', 'Crime', 'Shelter', 'Tent', 'Overdose']

    ### create products
    products = itertools.product(neighbourhoods, keywords)

    data = []
    ### run each product
    for keys in list(products):
        ### generate the search string with spaces
        search_string = " ".join(keys)

        # run the search
        data += run_search(search_string)

    ### create pandas df of all data
    #print(data)
    df = pd.DataFrame(data)

    ### remove duplicates

    ### write to csv
    filename = f"GVCEH-{str(datetime.date.today())}-tweet-raw.csv"
    df.to_csv(filename, encoding='utf-8')

    print(df.head(10))
    print(df.shape)
    #pprint(data)


    ## Count duplicates
    dups_color = df.pivot_table(columns=['tweet_id'], aggfunc='size')
    print (dups_color)

def main():
    search_by_neighbourhood_keyword_products()
    #search_by_crd_keyword_products()
    #search_by_influencer_keyword_products()
    #search_by_geolocation()

if __name__ == "__main__":
    main()
