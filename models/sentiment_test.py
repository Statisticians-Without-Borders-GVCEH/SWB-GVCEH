from transformers import pipeline
# from setfit import SetFitModel

pin_memory=False

    # create the model
model = pipeline("sentiment-analysis",
                     model='cardiffnlp/twitter-roberta-base-sentiment-latest',
                     device=-1
                     )
model.tokenizer.model_max_length = 512