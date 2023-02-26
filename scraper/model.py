from transformers import pipeline
from setfit import SetFitModel

def sentiment_model(df):
    # create the model ( #-1 = cpu, 0 = gpu )
    model = pipeline("sentiment-analysis",
                     model='cardiffnlp/twitter-roberta-base-sentiment-latest',
                     device=-1
                     )
    model.tokenizer.model_max_length = 512
    print("sentiment model downloaded")

    all_res = []
    for res in model(df.text.to_list(), batch_size=32, truncation=True):
        all_res.append(res)

    all_sentiments = [x['label'] for x in all_res]
    all_scores = [x['score'] for x in all_res]

    df['sentiment'] = all_sentiments
    df['score'] = all_scores
    print("sentiment scores added")
    return df

def relevance_model(df):
    # create the model
    model = SetFitModel.from_pretrained("sheilaflood/gvceh-setfit-rel-model2")
    all_text = df.text
    all_results = model(list(all_text))
    all_results = all_results.numpy()
    df = df[all_results == 1]  # filters out non-relevant tweets
    print("relevancy filter applied")
    return df