import requests
import json
import csv 
import datetime
import tweepy as tw
 
API_KEY = "" # consumer
API_SECRET_KEY = "" # consumer
BEARER_TOKEN = ""

ACCESS_TOKEN = ""
ACCESS_TOKEN_SECRET = ""

#url = "curl -X GET -H "Authorization: Bearer <BEARER TOKEN>" "https://api.twitter.com/2/tweets/20""

# https://datascienceparichay.com/article/python-get-data-from-twitter-api-v2/

search_query = "homelessness lang:en -is:retweet"
date_since = "2021-07-01"
start_date = datetime.datetime(2021, 7, 1, 0,0,0)

client = tw.Client(bearer_token=BEARER_TOKEN)

### time limits
start_time = "2021-07-01T00:00:00Z"
end_time = "2022-01-01T00:00:00Z"

# get tweets
tweets = client.search_recent_tweets(
    query=search_query,
    #start_time=start_time,
    #end_time=end_time,
    tweet_fields = ["created_at", "text", "source", "retweet_count"],
    user_fields = ["name", "username", "location", "verified", "description"],
    max_results = 10,
    expansions='author_id'
)

for tweet in tweets.data:
    print("="*40)
    print(tweet.text)
    #print(tweet.retweet_count)
