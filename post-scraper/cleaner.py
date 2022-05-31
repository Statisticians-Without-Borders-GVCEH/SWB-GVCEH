import glob
import os

import pandas as pd

### import the latest file 
list_of_files = glob.glob('../scraper/data/*') # * means all if need specific format then *.csv
latest_file = max(list_of_files, key=os.path.getctime)

### convert to pandas?
df = pd.read_csv(latest_file)


### remove duplicates

### exclude list

### fancy NLP stuff here?