import pandas as pd
import requests
import io
import os
# from dotenv import load_dotenv
from github import Github

# load_dotenv() #take environment variables from .env

USERNAME = os.environ["USERNAME"]
TOKEN = os.environ["TOKEN"]

g = Github(USERNAME, TOKEN)
user = g.get_user(USERNAME)
repo = user.get_repo('SWB-GVCEH')
# print(repo.full_name)

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
with open('../scraper/data/GVCEH-2022-05-23-tweet-raw.csv', 'r') as file:
    content = file.read()

# upload to github
git_file = 'modeling/data/GVCEH-2022-05-23-tweet-raw-duplicate.csv'
repo.create_file(git_file, "committing new file", content, branch="main")
print('done!!!')



