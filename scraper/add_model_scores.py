import os
import pandas as pd
pd.set_option('display.float_format', lambda x: '%.0f' % x)
import model  # gvceh functions

file = '../data/GVCEH-tweets-combined_2022-04-03.csv'
df = pd.read_csv(file)
df_scored = model.sentiment_model(df)
df_scored.to_csv('GVCEH-tweets-combined_2022-04-03_scored.csv', encoding='utf-8', float_format='%.0f')
