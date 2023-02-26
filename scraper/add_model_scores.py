import os
import pandas as pd
pd.set_option('display.float_format', lambda x: '%.0f' % x)
import model  # gvceh functions

file = '../data/cleaned/GVCEH-2022-07-25-tweet-cleaned.csv'
df = pd.read_csv(file)

df_scored = model.sentiment_model(df)
print(len(df))
df_scored_relevant = model.relevance_model(df)
print(len(df_scored_relevant))

# SAVE TO CSV AND DELETE CSV AFTER CONFIRMING FORMAT LOOKS GOOD
df_scored_relevant.to_csv('GVCEH-2022-07-25-tweet-scored.csv', encoding='utf-8', float_format='%.3f')
