import pandas as pd


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


if __name__ == "__main__":

    filename = "../data/post-scraper/GVCEH-2022-06-13-tweet-raw.csv"

    df = pd.read_csv(filename)

    df = clean_tweets(df)

    newname = filename.replace("raw", "cleaned")

    df.to_csv(newname)
