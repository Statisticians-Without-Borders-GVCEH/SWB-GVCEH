import datetime
import glob
import os
from github import Github
import pandas as pd

print("executing cleaner.py")

### import the latest file 
# list_of_files = glob.glob('./scraper/data/*.csv') # * means all if need specific format then *.csv
# latest_file = max(list_of_files, key=os.path.getctime)

# # Read from github
latest_file = f"GVCEH-{str(datetime.date.today())}-tweet-raw.csv"
with open(f'./scraper/data/{latest_file}', 'r') as file:
# with open('./scraper/data/GVCEH-2022-06-03-tweet-raw.csv', 'r') as file:
    df = pd.read_csv(file)

### convert to pandas?
# df = pd.read_csv(latest_file)
print(latest_file)
print(f"Original file: {len(df)} tweets")

### remove duplicates
df = df.drop_duplicates(subset=['tweet_id'], keep='last')

### exclude list
bad_words = ['Trump', 'Cuomo', 'SF', 'NYC']

for bad in bad_words:
    df = df[~df['text'].str.lower().str.contains(bad.lower())]

### fancy NLP stuff here?


# ### write out here#
# out_file = os.path.basename(latest_file).replace("raw", "cleaned")
# filename = f"data/{out_file}"

# print(out_file)
# df.to_csv(filename, encoding='utf-8', index=False)

# print(f"Cleaned file: {len(df)} tweets")
# print("Done Cleaning")  

# open github api connection
USERNAME = os.environ["USERNAME"] # for github api
TOKEN = os.environ["TOKEN"] # for github api

g = Github(USERNAME, TOKEN)
user = g.get_user(USERNAME)
repo = user.get_repo('SWB-GVCEH')
    
# upload to github
filename = f"GVCEH-{str(datetime.date.today())}-tweet-cleaned.csv"
df_csv = df.to_csv()
git_file = f'post-scraper/data/{filename}'
repo.create_file(git_file, "committing new file", df_csv, branch="main")
print("Done Cleaning") 

# Testing if upload is complete
with open(f'./post-scraper/data/{filename}', 'r') as file:
    df = pd.read_csv(file)
    print(df)
