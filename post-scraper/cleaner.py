import glob
import os

import pandas as pd

print("executing cleaner.py")

### import the latest file 
list_of_files = glob.glob('./scraper/data/*.csv') # * means all if need specific format then *.csv
latest_file = max(list_of_files, key=os.path.getctime)
print(f"latest file: {latest file}")

### convert to pandas?
df = pd.read_csv(latest_file)
print(f"Original file: {len(df)} tweets")

### remove duplicates
df = df.drop_duplicates(subset=['tweet_id'], keep='last')

### exclude list
bad_words = ['Trump', 'Cuomo', 'SF', 'NYC']

for bad in bad_words:
    df = df[~df['text'].str.lower().str.contains(bad.lower())]

### fancy NLP stuff here?


### write out here#
out_file = os.path.basename(latest_file).replace("raw", "cleaned")
filename = f"data/{out_file}"

print(out_file)
df.to_csv(filename, encoding='utf-8', index=False)

print(f"Cleaned file: {len(df)} tweets")
print("Done Cleaning")   
