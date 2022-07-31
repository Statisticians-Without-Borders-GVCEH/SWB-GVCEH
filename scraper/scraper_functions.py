import pandas as pd
import io
from github import Github


def update_file_in_github(USERNAME, TOKEN, git_file, df_new):

    df_new = df_new[["text", "scrape_time", "tweet_id", "created_at", "reply_count", "quote_count",
                     "like_count", "retweet_count", "geo_full_name", "geo_id", "username", "num_followers",
                     "search_keywords", "search_neighbourhood", "sentiment", "score"]]

    print('New Tweets: ', df_new.shape)

    # open github api connection
    g = Github(USERNAME, TOKEN)
    user = g.get_user(USERNAME)
    repo = user.get_repo("SWB-GVCEH")

    # Read CSV from Github -> Dataframe
    # contents = repo.get_contents("")
    contents = repo.get_contents(git_file)
    print(contents)

    stuff = contents.decoded_content
    df_old = pd.read_csv(io.StringIO(stuff.decode('utf-8')))

    df_old = df_old[["text", "scrape_time", "tweet_id", "created_at", "reply_count", "quote_count",
             "like_count", "retweet_count", "geo_full_name", "geo_id", "username", "num_followers",
             "search_keywords", "search_neighbourhood", "sentiment", "score"]]
    print('Original CSV: ', df_old.shape)

    df_merged = pd.concat([df_old, df_new]).drop_duplicates(subset='tweet_id', keep="last").reset_index(drop=True)
    print('Combined CSVs: ', df_merged.shape)


    # Convert DF back to CSV
    df_csv = df_merged.to_csv()

    repo.update_file(path=git_file, message="Adding new tweets", sha=contents.sha, branch="main", content=df_csv)

    print("File Updated in Github!")






