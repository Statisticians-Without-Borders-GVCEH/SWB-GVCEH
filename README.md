# SWB-GVCEH
Statisticians Without Borders sentiment analysis project for GVCEH


This project collects data from Twitter daily using the Twitter API and performs sentiment analysis using python/NLTK. 


Automation:
GitHub actions triggers the scraper.py to be run every night at 8pm PCT (3 UTC). The lookback period for the scraper is 48 hours; new tweets are deduped against historical tweets, which are stored in the SWB-GVCEH/data/processed/twitter/github_actions folder. If the latest file exceeds 5MB, a new csv file is created in the folder listed above and the tweets are saved there. If the file is less than 5MB the new tweets are added to the latest csv. 


