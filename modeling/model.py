import os
import pandas as pd
import requests
import io

url = 'https://raw.githubusercontent.com/sheilaflood/SWB-GVCEH/main/scraper/data/'
file = 'GVCEH-2022-04-10-tweet-raw.csv'
old_url = url + file


read_data = requests.get(old_url).content
df = pd.read_csv(io.StringIO(read_data.decode('utf-8')))
print(df.head())


new_url = url.replace('scraper', 'modeling')
new_file = file.replace('raw.csv', 'scored.csv')

requests.post(new_url, data = df.to_csv(new_file))

print('Done!')
