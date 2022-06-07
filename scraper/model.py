from transformers import pipeline

def sentiment_model(df):
    # create the model
    model = pipeline("sentiment-analysis",
                     model='cardiffnlp/twitter-roberta-base-sentiment-latest',
                     device=0
                     )
    model.tokenizer.model_max_length = 512

    all_res = []
    for res in model(df.text.to_list(), batch_size=32, truncation=True):
        all_res.append(res)

    all_sentiments = [x['label'] for x in all_res]
    all_scores = [x['score'] for x in all_res]

    df['sentiment'] = all_sentiments
    df['score'] = all_scores
    return df