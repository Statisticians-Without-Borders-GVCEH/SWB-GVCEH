def clean_tweets(df):
    print("Cleaning Tweets...")
    print(f"Original file: {len(df)} tweets")

    ### remove duplicates
    df = df.drop_duplicates(subset=['tweet_id'], keep='last')

    ### exclude list
    bad_words = ['Trump', 'Cuomo', 'SF', 'NYC']

    for bad in bad_words:
        df = df[~df['text'].str.lower().str.contains(bad.lower())]

    ### fancy NLP stuff here?


    return df