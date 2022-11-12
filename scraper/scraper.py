import datetime
import os
import pickle
import os.path
import time

import model  # gvceh functions
import cleaner  # gvceh functions
import scraper_functions  # gvceh functions
import tweepy as tw
import pandas as pd
import sys
import io

from github import Github

from transformers import pipeline

from pprint import pprint
import dotenv

### setting up the config
MAX_TWEETS = 100  # if we want to return less than the API's max
QUERY_START_AT = 0


def query_twitter(TW_QUERY, RELEVANT_REGION, START_TIME, END_TIME, SEVEN_DAYS=False):
    """
    Run one query against the API and store it
    """

    return_data = []
    search_query = TW_QUERY.replace(" and ", ' "and" ')

    #     print("=" * 40)
    #     print(f"Searching for... {search_query}")
    # print("Searching...")
    # print(TW_QUERY)

    if SEVEN_DAYS:
        START_TIME = None
        END_TIME = None

    # get tweets
    ### limits us last 7 days, need elevated account for longer than that
    tweets = client.search_recent_tweets(
        query=search_query,
        start_time=START_TIME,
        end_time=END_TIME,
        tweet_fields=[
            "context_annotations",
            "public_metrics",
            "created_at",
            "text",
            "source",
            "geo",
        ],
        user_fields=[
            "name",
            "username",
            "location",
            "verified",
            "description",
            "public_metrics",
        ],
        max_results=MAX_TWEETS,
        place_fields=["country", "geo", "name", "place_type"],
        expansions=["author_id", "geo.place_id", "referenced_tweets.id"],
    )

    ### not yielding anything? exit early
    if not tweets.data:
        print("Sorry, no results found")
        return []

    ### generate our place information
    if "places" in tweets.includes.keys():
        place_info = {
            place.id: {
                "bbox": place.geo[
                    "bbox"
                ],  # geoJSON, min long, min lat, max long, max lat
                "full_name": place.full_name,
                # place.name
                # place.place_type
                # place.full_name
                # place.country
            }
            for place in tweets.includes["places"]
        }

        ### generate our twitter twitter
    for tweet, user in zip(tweets.data, tweets.includes["users"]):

        newtweet = {}

        # original text
        newtweet["text"] = tweet.text

        ### working on quote tweets:
        if tweet.referenced_tweets:
            # print(tweet.text)
            for thist in tweet.referenced_tweets:
                if thist.data["type"] == "quoted":
                    qt = client.get_tweet(thist.data["id"], tweet_fields=["text"])

                    mergetweet = (
                        newtweet["text"].strip() + " " + qt.data["text"].strip()
                    )
                    mergetweet = mergetweet.replace("\n", "")

                    newtweet["text"] = mergetweet

        ### scrape time
        newtweet["scrape_time"] = str(datetime.datetime.now())

        ### unique ID
        newtweet["tweet_id"] = tweet.id

        # post time
        newtweet["created_at"] = str(tweet.created_at)

        # reply count
        newtweet["reply_count"] = tweet.public_metrics["reply_count"]
        # number of quote tweets
        newtweet["quote_count"] = tweet.public_metrics["quote_count"]
        # number of likes
        newtweet["like_count"] = tweet.public_metrics["like_count"]
        # number of RTs
        newtweet["retweet_count"] = tweet.public_metrics["retweet_count"]

        ### geo twitter (where available)
        newtweet["geo_full_name"] = None
        newtweet["geo_id"] = None
        newtweet["geo_bbox"] = None

        if tweet.geo:
            newtweet["geo_id"] = tweet.geo["place_id"]
            newtweet["geo_full_name"] = place_info[tweet.geo["place_id"]]["full_name"]
            newtweet["geo_bbox"] = place_info[tweet.geo["place_id"]]["bbox"]

        ### cordinate twitter - where available
        newtweet["tweet_coordinate"] = ""
        if tweet.geo:
            if tweet.geo.get("coordinates", None):
                newtweet["tweet_coordinate"] = tweet.geo.get("coordinates").get(
                    "coordinates"
                )

        # poster
        newtweet["username"] = user.username

        ### user profile location
        newtweet["user_location"] = user.location

        # number of followers
        newtweet["num_followers"] = user.public_metrics["followers_count"]

        ### so we know how it was found
        newtweet["search_keywords"] = search_query

        ### more meta twitter
        newtweet["search_neighbourhood"] = RELEVANT_REGION

        return_data.append(newtweet)

    return return_data


def batch_scrape(SEVEN_DAYS=False):
    ### open our pickle cache of queries
    # https://stackoverflow.com/questions/25464295/dump-a-list-in-a-pickle-file-and-retrieve-it-back-later
    with open(QUERY_CACHE_FILE, "rb") as f:
        query_cache = pickle.load(f)

    ### manage the pickle json twitter for state status
    ### first day today?  yes or no
    ### yes -> going to have to create a new CSV
    ### no -> take inrement

    ### probably manage the twitter file

    ### figure out what attempt at scraping this is?
    # job_n = 0
    # print(f"Batch job #{job_n} today.")

    num_queries = 0
    num_results = 0

    ### pull those n queries
    # our_queries = query_cache[MAX_PER_15*job_n : MAX_PER_15 * (job_n+1)]

    ### because of batching, we want to run as many queries as we can
    ### when we break -> store that query number, so next time we start there
    ### TODO: STORE ON BREAK
    our_queries = query_cache[QUERY_START_AT:]

    dtformat = "%Y-%m-%dT%H:%M:%SZ"
    current_time = datetime.datetime.utcnow()
    start_time = current_time - datetime.timedelta(days=2)

    # Subtracting 15 seconds because api needs end_time must be a minimum of 10
    # seconds prior to the request time
    end_time = current_time - datetime.timedelta(seconds=15)

    # convert to strings
    start_time, end_time = start_time.strftime(dtformat), end_time.strftime(dtformat)

    flag = 1
    for q in our_queries:

        num_queries += 1

        try:

            ### pass to scrape
            ### scrape and save

            data = query_twitter(q[0], q[1], start_time, end_time, SEVEN_DAYS)

            num_results += len(data)

            ### scave our twitter - only if we got any
            if data:
                data_cleaned = [
                    {
                        k: v
                        for k, v in d.items()
                        if k not in ("geo_bbox", "tweet_coordinate")
                    }
                    for d in data
                ]
                df = pd.DataFrame(data_cleaned)

                if flag == 1:
                    final_results = df
                    flag -= 1

                final_results = pd.concat([final_results, df])
                print(final_results.tail())

        except Exception as e:

            print("Broke on...")
            print(f"Query # {num_queries}")
            print(f"Returned {num_results} tweets")
            print(str(e))
            # input()
            break

        time.sleep(2.5)

    ### update scrape info
    return final_results


if __name__ == "__main__":
    ### TODO: args to switch these
    ### TODO: command line blow out delete

    # determine if script includes parameters or not
    # total arguments
    n = len(sys.argv)
    print("Total arguments passed:", n)

    print("\nArguments passed:", end=" ")
    for i in range(0, n):
        print(sys.argv[i], end=" ")

    if n > 1:
        print("More than 1 parameter passed; Running via Github Actions")
        API_KEY = os.environ["API_KEY"]
        API_SECRET_KEY = os.environ["API_SECRET_KEY"]
        BEARER_TOKEN = os.environ["BEARER_TOKEN"]
        ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
        ACCESS_TOKEN_SECRET = os.environ["ACCESS_TOKEN_SECRET"]

        USERNAME = os.environ["USERNAME"]  # for github api
        TOKEN = os.environ["TOKEN"]  # for github api

        QUERY_CACHE_FILE = "scraper/querylist.pkl"

        SEVEN_DAYS = False

    else:
        print("Less than 1 parameter passed; Running manually ")
        dotenv.load_dotenv()  # imprt out enviroment variables

        API_KEY = os.environ.get("API_KEY")  # consumer
        API_SECRET_KEY = os.environ.get("API_SECRET_KEY")  # consumer
        BEARER_TOKEN = os.environ.get("BEARER_TOKEN")

        ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
        ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")

        QUERY_CACHE_FILE = "querylist.pkl"

        SEVEN_DAYS = True

    # twitter api
    client = tw.Client(bearer_token=BEARER_TOKEN)
    final_results = batch_scrape(SEVEN_DAYS)
    if n > 1:
        ### Don't have CUDA installed, can't run the model
        final_results = model.sentiment_model(final_results)  # adding model scores
    df_new = cleaner.clean_tweets(final_results)  # post-scraping cleaner

    if n > 1:
        git_file = "data/processed/twitter/github_actions"
        scraper_functions.update_file_in_github(USERNAME, TOKEN, git_file, df_new)
    else:
        # Save new file locally
        filename = f"../data/processed/twitter/GVCEH-{str(datetime.date.today())}-tweet-scored.csv"

        if os.path.isfile(filename):
            df_new.to_csv(
                filename, encoding="utf-8", mode="a", header=False, index=False
            )
        else:
            df_new.to_csv(filename, encoding="utf-8", index=False)
