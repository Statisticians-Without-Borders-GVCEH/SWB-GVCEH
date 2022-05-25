import os
import pandas as pd

# path = '../scraper/data/'
path = os.path.dirname(os.path.abspath(__file__))
path = path.replace('modeling', 'scraper/data/')
print(path)
files = os.listdir(path)
last_file_path = path + files[-1]
df = pd.read_csv(last_file_path)


new_file_path = last_file_path.replace('scraper', 'modeling').replace('raw.csv', 'scored.csv')
df.to_csv(new_file_path)
print('done!')
