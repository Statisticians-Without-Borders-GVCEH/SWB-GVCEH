#sharepoint connection
import pandas as pd
import json
from shareplum import Site
from shareplum import Office365
from shareplum.site import Version
from io import BytesIO

# create a sharepoint_cred.json file in the dashboard directory with two key-value pairs - username and password
with open('./dashboard/sharepoint_cred.json') as creds:
    parsed = json.load(creds)

username = parsed['username']
password =  parsed['password']

def get_data_sharepoint():

    authcookie = Office365('https://victoriahomelessness.sharepoint.com', username=username, password=password).GetCookies()
    site = Site('https://victoriahomelessness.sharepoint.com/sites/SocialMediaSentimentAnalysisCollaboration', version=Version.v365, authcookie=authcookie)

    folder = site.Folder('Shared Documents/dummy_data')

    test = folder.get_file('Tweets.csv')

    df = pd.read_csv(BytesIO(test), parse_dates=['tweet_created'], dtype={'tweet_id':object})

    return df

# print(get_data_sharepoint())
