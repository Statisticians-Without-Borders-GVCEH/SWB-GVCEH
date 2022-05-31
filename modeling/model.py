import pandas as pd
import requests
import io
import os
# from dotenv import load_dotenv
from github import Github
import csv
import tensorflow
from transformers import pipeline


# load_dotenv() #take environment variables from .env

# load environment variables
USERNAME = os.environ["USERNAME"]
TOKEN = os.environ["TOKEN"]

# create the model
model = pipeline("sentiment-analysis",
                 model='cardiffnlp/twitter-roberta-base-sentiment-latest',
                 device=0
                 )
model.tokenizer.model_max_length = 512

# open github api connection
g = Github(USERNAME, TOKEN)
user = g.get_user(USERNAME)
repo = user.get_repo('SWB-GVCEH')
my_repo = g.get_repo(repo.full_name)


contents = my_repo.get_contents("")
all_files = []
while contents:
    file_content = contents.pop(0)
    if file_content.type == "dir":
        contents.extend(repo.get_contents(file_content.path))
    else:
        file = file_content
        all_files.append(str(file).replace('ContentFile(path="','').replace('")',''))

# Read from github
with open('./scraper/data/GVCEH-2022-05-30-tweet-raw.csv', 'r') as file:
    df = pd.read_csv(file)
    # print(df.info())

all_res = []
for res in model(df.text.to_list(), batch_size=32, truncation=True):
  all_res.append(res)

all_sentiments = [x['label'] for x in all_res]
all_scores = [x['score'] for x in all_res]

df['sentiment'] = all_sentiments
df['score'] = all_scores
df.head()

stuff = df.to_csv()

# upload to github
git_file = 'modeling/data/GVCEH-2022-05-30-tweet-scored.csv'
repo.create_file(git_file, "committing new file", stuff, branch="main")
print('Done!!!')
