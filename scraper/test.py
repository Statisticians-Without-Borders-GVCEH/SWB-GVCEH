import datetime
import os
import pickle
import os.path
import time
import model  # gvceh functions
import cleaner  # gvceh functions
import tweepy as tw
import pandas as pd
import io
import requests

from github import Github
from transformers import pipeline

from pprint import pprint
import dotenv



USERNAME = os.environ["USERNAME"]  # for github api
TOKEN = os.environ["TOKEN"]  # for github api

# open github api connection
g = Github(USERNAME, TOKEN)
user = g.get_user(USERNAME)
repo = user.get_repo("SWB-GVCEH")


print("READING CSV FROM GITHUB")
consolidated_file_path = 'https://github.com/sheilaflood/SWB-GVCEH/blob/main/data/processed/twitter/GVCEH-tweets-combined.csv'
s=requests.get(consolidated_file_path).content
c=pd.read_csv(io.StringIO(s.decode('utf-8')))

print("Updating same file") 
df_csv = c.to_csv()
repo.update_file(consolidated_file_path, "Adding new tweets", df_csv, branch="main")
print("Done with scraper.py!!!")
