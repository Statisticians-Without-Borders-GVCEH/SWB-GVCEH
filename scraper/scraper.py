import datetime
import os
import pickle
import os.path
import time

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


MAX_PER_15 = 9999 ### TODO: Find this limit
QUERY_START_AT = 0

QUERY_MAX_LENGTH = 512
SUB_QUERY_CHUNKS = 10 ### how many queries we split Appendix C + E + D into
NUM_ACCOUNTS_TO_TARGET = 5 ### How many queries we split Appendix B into
NEIGHBOURHOOD_CHUNKS = 10 ### split neighbourhood into how many chunks ?
QUERY_CACHE_FILE = "querylist.pkl"


client = tw.Client(bearer_token=BEARER_TOKEN)

#url = "curl -X GET -H "Authorization: Bearer <BEARER TOKEN>" "https://api.twitter.com/2/tweets/20""

# https://datascienceparichay.com/article/python-get-data-from-twitter-api-v2/
# tweepy / api v2 info

def query_twitter(TW_QUERY, RELEVANT_REGION):
    """ 
        Run one query against the API and store it
    """

    return_data = []
    search_query = TW_QUERY.replace(' and ', ' "and" ')

    print("="*40)
    print(f"Searching for... {search_query}")

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
    if not tweets.data: 
        print("Sorry, no results found")
        return []

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

    ### generate our twitter data
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
        newtweet['tweet_coordinate'] = ''
        if tweet.geo:
            if tweet.geo.get('coordinates', None):
                newtweet['tweet_coordinate'] = tweet.geo.get('coordinates').get('coordinates')

        # poster
        newtweet['username'] = user.username

        # number of followers
        newtweet['num_followers'] = user.public_metrics['followers_count']

        ### so we know how it was found
        newtweet['search_keywords'] = search_query

        ### more meta data
        newtweet['search_neighbourhood'] = RELEVANT_REGION

        return_data.append(newtweet)

    return return_data

def save_results(RESULTS):
    #pprint(RESULTS)

    ### create pandas df of all data
    df = pd.DataFrame(RESULTS)

    ### remove duplicates

    ### write to csv
    filename = f"data/GVCEH-{str(datetime.date.today())}-tweet-raw.csv"

    if os.path.isfile(filename):
        df.to_csv(filename, encoding='utf-8', mode='a', header=False, index=False)
    else:
        df.to_csv(filename, encoding='utf-8', index=False)

    print(df.head(10))
    print(df.shape)

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

def prep_subq(KEYWORDS_DICT, CHUNKS):
    """
        Generates the list of strings
        Each string is the keyword subquery
    """
    ### make one list of keywords
    if type(KEYWORDS_DICT) is not list:
        allkw = sum(KEYWORDS_DICT.values(), [])
    else:
        allkw = KEYWORDS_DICT

    ### chunk it down, we can't exceed 512 character a query
    allkw = [allkw[i::CHUNKS] for i in range(CHUNKS)]

    subq = []

    for a in allkw: 
        ### we use OR to help reduce number of queries
        subq.append(" OR ".join(a))

    return subq

def gen_query_one(SUB_QUERY):
    """
        Generates a list of queries containing neighbourhood x keyword products
    """

    ### get our neighbourhoods
    data = pd.read_csv('../data/appendices/aa_old.csv', index_col=0)

    neighbourhoods = [n.strip().lower() for n in data.Location.tolist()]

    neighbourhoods = prep_subq(neighbourhoods, NEIGHBOURHOOD_CHUNKS)

    ### now to make our queries with the neighbourhoods
    query1 = []

    for n in neighbourhoods:
        for kws in SUB_QUERY:
            querytext = f"({n}) ({kws}) lang:en -is:retweet"
            if len(querytext) > QUERY_MAX_LENGTH: 
                print("WARNING: QUERY 1 TOO LARGE")
                print("CHUNK KEYWORD UNION SMALLER")
            #max = len(querytext) if len(querytext) > max else max
            query1.append((querytext, n))

    #print(max)

    ### returing a list of queries from this product
    return query1

def gen_query_two(SUB_QUERY):
    """
        Generate list of CRD identifies x keywords 
    """

    ### our CRD level keywords
    neighbourhoods = [
        'Greater Victoria', '#GreaterVictoria', 'Victoria', 'VictoriaBC', 
        'Victoria B.C.', '#YYJ', 'YYJ', '#GVCEH', 
        'Greater Victoria Coalition to End Homelessness'
    ]

    ### now to make our queries with the neighbourhoods
    query = []

    for n in neighbourhoods:
        for kws in SUB_QUERY:
            querytext = f"{n} ({kws}) lang:en -is:retweet"
            if len(querytext) > QUERY_MAX_LENGTH: 
                print("WARNING: QUERY 2 TOO LARGE")
                print("CHUNK KEYWORD UNION SMALLER")
                print(querytext)
                print(len(querytext))
            query.append((querytext, n))

    ### returing a list of queries from this product
    return query
    
def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

def gen_query_three(SUB_QUERY):
    """
        Check specific twitter accounts for tweets
    """

    ### load the names from the appendix
    data = pd.read_csv('../data/appendices/aborganizations.csv', index_col=0)

    orgs = [n.strip().lower() for n in data.Organizations.tolist()]

    data = pd.read_csv('../data/appendices/abpersons.csv', index_col=0)

    pers = [n.strip().lower() for n in data.Influencers.tolist()]

    ### loop through like above to generate queries
    query = []

    for grp in chunker(orgs+pers, NUM_ACCOUNTS_TO_TARGET):

        subtext = []
        for name in grp:
            subtext.append(f"from:{name}")

        subtext = " OR ".join(subtext)

        for kws in SUB_QUERY:
            querytext = f"({subtext}) ({kws}) lang:en -is:retweet"
            if len(querytext) > QUERY_MAX_LENGTH: 
                print("WARNING: QUERY 3 TOO LARGE")
                print("CHUNK KEYWORD UNION SMALLER")
                print(querytext)
                print(len(querytext))
            query.append((querytext, 'individual'))

    return query

def gen_queries():
    # load keywords
    keywords = load_keywords()

    ### generate query keyword paramteres
    ### prep keyword union
    subq = prep_subq(keywords, SUB_QUERY_CHUNKS)

    # query 1 - neighbourhood keyword products 
    print("Generating Query 1...")
    q1 = gen_query_one(subq)

    # query 2 - CRD keyword products
    print("Generating Query 2...")
    q2 = gen_query_two(subq)

    # query 3 - account keyword products
    print("Generating Query 3")
    q3 = gen_query_three(subq)

    # query 4 - geotagged tweets
    q4 = []

    ### combine
    queries = q1 + q2 + q3 + q4

    print(f"Total # of queries: {len(queries)}")
    print(f"Will take {len(queries) / MAX_PER_15} attempts")

    # cache queries
    print("Writing...")
    with open(QUERY_CACHE_FILE, 'wb') as f:
        pickle.dump(queries, f)

def batch_scrape():

    ### open our pickle cache of queries
    # https://stackoverflow.com/questions/25464295/dump-a-list-in-a-pickle-file-and-retrieve-it-back-later
    with open(QUERY_CACHE_FILE, 'rb') as f:
        query_cache = pickle.load(f)

    ### manage the pickle json data for state status
    ### first day today?  yes or no
    ### yes -> going to have to create a new CSV
    ### no -> take inrement

    ### probably manage the data file

    ### figure out what attempt at scraping this is?
    #job_n = 0
    #print(f"Batch job #{job_n} today.")

    num_queries = 0
    num_results = 0

    ### pull those n queries
    #our_queries = query_cache[MAX_PER_15*job_n : MAX_PER_15 * (job_n+1)]

    ### because of batching, we want to run as many queries as we can
    ### when we break -> store that query number, so next time we start there
    ### TODO: STORE ON BREAK
    our_queries = query_cache[QUERY_START_AT:]

    for q in our_queries:

        num_queries += 1

        try:

            ### pass to scrape
            ### scrape and save
            data = query_twitter(q[0], q[1])

            num_results += len(data)

            ### scave our data - only if we got any
            if data: save_results(data)

        except Exception as e:

            print("Broke on...")
            print(f"Query # {num_queries}")
            print(f"Returned {num_results} tweets")
            print(str(e))
            #input()
            break

        time.sleep(1)

    ### update scrape info

if __name__ == "__main__":
    ### TODO: args to switch these
    ### TODO: command line blow out delete

    ### gen_queries
    #gen_queries()

    ### batch scrape
    batch_scrape()