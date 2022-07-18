import pandas as pd
import glob
import datetime as datetime


def clean_tweets(df):
    print("Cleaning Tweets...")
    print(f"Original file: {len(df)} tweets")

    ### remove duplicates
    df = df.drop_duplicates(subset=["tweet_id"], keep="last")

    ### exclude list
    bad_words = ["Trump", "Cuomo", "SF", "NYC"]

    for bad in bad_words:
        df = df[~df["text"].str.lower().str.contains(bad.lower())]

    ### fancy NLP stuff here?

    ### add the influencer flag here if data source is Twitter
    # twitter_influencer_list = list(pd.read_csv('./dashboard/influencers.csv')['handle'])
    # df['influencer_flag'] = df['username'].apply(lambda x: 1 if x in twitter_influencer_list else 0)

    print(f"Cleaned file: {len(df)} tweets")
    return df


def clean_csv():
    """
    Opens up a csv,
    cleans it
    writes new file
    """
    filename = "../data/scraped/GVCEH-2022-07-18-tweet-raw.csv"
    # filename = "../data/post-scraper/all-raw-merged-2022-06-22.csv" # merged data

    df = pd.read_csv(filename)

    df = clean_tweets(df)

    newname = filename.replace("raw", "cleaned")
    newname = newname.replace("scraped", "cleaned")

    ### being lazy and just overwriting
    # newname = "../data/cleaned/all-cleaned-merged-2022-06-22.csv" # for merged data

    df.to_csv(newname)


def merge_all_raw_data():
    """
    Opens all raw data csvs
    merges into a single file
    """

    print("Merging...")

    files = glob.glob("../data/scraped/*raw*.csv")

    ### read in first csv
    df = pd.read_csv(files[0])

    for f in files[1:]:
        print(f)

        ### load in the csv
        newdf = pd.read_csv(f)

        ### append to existing
        df = pd.concat([df, newdf])

    ### output / save
    newfile = f"../data/post-scraper/all-raw-merged-{str(datetime.date.today())}.csv"

    df.to_csv(newfile, encoding="utf-8")

    print(df.head(20))
    print(df.size)


if __name__ == "__main__":
    # TODO: @click to switch
    clean_csv()

    # merge_all_raw_data()
