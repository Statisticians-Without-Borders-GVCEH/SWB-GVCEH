import pandas as pd
import requests
import io

# ssl._create_default_https_context = ssl._create_unverified_context

username = 'sheilaflood'
token = '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'

github_session = requests.Session()
github_session.auth = (username, token)


url = 'https://raw.githubusercontent.com/sheilaflood/SWB-GVCEH/main/scraper/data/'
file = 'GVCEH-2022-04-10-tweet-raw.csv'
old_url = url + file

download = github_session.get(old_url).content
df = pd.read_csv(io.StringIO(download.decode('utf-8')))
print(df.head())


new_url = url.replace('scraper', 'modeling')
new_file = file.replace('raw.csv', 'scored.csv')
print(new_url + new_file)

github_session.post(new_url, data = df.to_csv(new_file))

print('Done!')



