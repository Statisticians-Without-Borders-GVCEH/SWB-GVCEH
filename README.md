# SWB-GVCEH

Summary: Statisticians Without Borders sentiment analysis project for GVCEH. This project collects data from Twitter daily using the Twitter API and performs sentiment analysis & relevancy classification on tweets. 


Automation:
GitHub actions triggers the scraper.py script to be run every night at 8pm PCT (3 UTC). The lookback period for the scraper is 48 hours. New tweets are deduped against historical tweets, which are stored in the SWB-GVCEH/data/processed/twitter/github_actions folder. If the latest file exceeds 5MB, a new csv file is created in the folder listed above and the tweets are saved there. If the file is less than 5MB the new tweets are added to the latest csv.

Modeling: 2 models (a sentiment model and relevance model) are used in this project. The sentiment model needed no additional training while the relevancy model was further trained using historical data from this project.  

Dashboard: The dashboard is built and hosted using streamlit (https://statisticians-without-borders-gvceh-swb--dashboardmockup-9l8zxx.streamlit.app/). To run the app locally, one should navigate to the parent dir and execute the following command: streamlit run ./dashboard/mockup.py


