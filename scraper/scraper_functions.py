import pandas as pd
import io
from github import Github
import base64
import datetime


def update_file_in_github(USERNAME, TOKEN, git_file, df_new):
    columns = ["text", "scrape_time", "tweet_id", "created_at", "reply_count", "quote_count",
               "like_count", "retweet_count", "geo_full_name", "geo_id", "username", "num_followers",
               "search_keywords", "search_neighbourhood", "sentiment", "score"]

    df_new = df_new[columns]
    print('New Tweets: ', df_new.shape)

    g = Github(USERNAME, TOKEN)
    user = g.get_user(USERNAME)
    repo = user.get_repo("SWB-GVCEH")

    # find latest file in repo that meets conditions... if > 20MB create new file
    files = []
    for file in repo.get_contents(git_file):
        files.append(file)
    last_file = files[-1]
    second_to_last_file = files[-2]

    last_file_MB = round((last_file.size / 1048576), 2)  # convert bits to MB
    print("Current CSV: ", last_file.path, " - ", last_file_MB, "MB")

    # Read CSV from Github -> Dataframe
    # contents.decode doesn't work if file > 1 MB; must use .get_git_blob()
    contents = repo.get_contents(last_file.path)
    blob = repo.get_git_blob(contents.sha)
    b64_decoded = base64.b64decode(blob.content).decode("utf8")
    df_old = pd.read_csv(io.StringIO(b64_decoded))
    df_old = df_old[columns]
    print('Current CSV: ', df_old.shape)

    if last_file_MB > 1:
        print("Latest file size exceeds limit - creating new csv...")

        # dedupe new data against last file in repo; don't keep any duplicates
        df_merged = pd.concat([df_old, df_new]).drop_duplicates(subset='tweet_id', keep=False).reset_index(drop=True)

        # dedupe new data against second to last file in repo; don't keep any duplicates
        contents = repo.get_contents(second_to_last_file.path)
        blob = repo.get_git_blob(contents.sha)
        b64_decoded = base64.b64decode(blob.content).decode("utf8")
        df_old = pd.read_csv(io.StringIO(b64_decoded))
        df_old = df_old[columns]
        df_merged = pd.concat([df_old, df_merged]).drop_duplicates(subset='tweet_id', keep=False).reset_index(drop=True)

        print('New Unique Tweets: ', df_merged.shape)

        df_csv = df_merged.to_csv()
        new_file = f'data/processed/twitter/GVCEH-tweets-combined_{str(datetime.date.today())}.csv'
        repo.create_file(path=new_file, message="Creating new csv", branch="main", content=df_csv)
        print(f"{new_file} created in Github")

    else:

        # dedupe against old data; keep 1 copy of each row if duplicates exist then replace existing csv
        df_merged = pd.concat([df_old, df_new]).drop_duplicates(subset='tweet_id', keep="last").reset_index(drop=True)
        df_csv = df_merged.to_csv()

        repo.update_file(path=last_file.path, message="Adding new tweets", sha=contents.sha, branch="main",
                         content=df_csv)
        print(f"{last_file} updated in Github!")


"""
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
    contents = repo.get_contents(git_file)

    ## contents.decode doesn't work if file > 1 MB
    # stuff = contents.decoded_content
    # df_old = pd.read_csv(io.StringIO(contents.decode('utf-8')))
    blob = repo.get_git_blob(contents.sha)
    b64 = base64.b64decode(blob.content)
    b64_decoded = b64.decode("utf8")
    df_old = pd.read_csv(io.StringIO(b64_decoded))

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
"""






