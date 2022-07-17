import gvceh_functions as gvceh
# import pytest
from datetime import datetime, date


def test_get_prior_period_unequal():
    start = datetime.strptime('2022-07-07', '%Y-%m-%d').date()
    end = datetime.strptime('2022-07-14', '%Y-%m-%d').date()
    prev_start, prev_end = gvceh.get_prior_period()

    assert(prev_start == datetime.strptime('2022-06-29', '%Y-%m-%d').date())
    assert(prev_end == datetime.strptime('2022-07-06', '%Y-%m-%d').date())

def test_get_prior_period_equal():
    start = datetime.strptime('2022-07-07', '%Y-%m-%d').date()
    end = datetime.strptime('2022-07-07', '%Y-%m-%d').date()
    prev_start, prev_end = gvceh.get_prior_period()

    assert(prev_start == datetime.strptime('2022-07-06', '%Y-%m-%d').date())
    assert(prev_end == datetime.strptime('2022-07-06', '%Y-%m-%d').date())


def test_agg_sentiments_by_category_calc():
    cdf = pd.read_csv('./data/test_agg_sentiments_by_category_cdf.csv')
    pdf = pd.DataFrame('./data/test_agg_sentiments_by_category_pdf.csv')

    actual_df = agg_sentiments_by_category(cdf, pdf)

    expected_df = pd.DataFrame({'Sentiment': ['Positive', 'Neutral', 'Negative'],
                                'Current': [6, 5, 7],
                                'Prior': [2, 5, 6] })
    
    assert(actual_df.equals(expected_df))

def test_agg_sentiments_by_category_counts():
    cdf = pd.read_csv('./data/test_agg_sentiments_by_category_cdf.csv')
    pdf = pd.DataFrame('./data/test_agg_sentiments_by_category_pdf.csv')

    actual_df = agg_sentiments_by_category(cdf, pdf)

    expected_df = pd.DataFrame({'Sentiment': ['Positive', 'Neutral', 'Negative'],
                                'Current': [6, 5, 7],
                                'Prior': [2, 5, 6] })
    
    assert(actual_df['Current'].sum() == len(cdf))
    assert(actual_df['Prior'].sum() == len(pdf))
    

def test_top_influencers():

    cdf = pd.read_csv('./data/test_agg_sentiments_by_category_cdf.csv')

    actual_df = top_influencers()
    expected_df = pd.DataFrame({'username': ['EpilepsyRUK', 'CharlesBodi', 'EndZonerBoner', 'PridgeWessea',
                                            'brightsider123', 'Andrewj60215382', 'LadyOfTheOcean1', 'Covid_Stinks',
                                            'ShellyRKirchoff', 'victoriacitro', 'Vickie627', 'drobwlldiad',
                                            'niMUSHIN', 'Silver_Strike', 'NanetteDonnelly', 'wendihouse22',
                                            'GFenburn', 'HatedByBCgovt'],
                                'tweet_id': [1]*18,
                                'reply_count': [5, 1, 2, 2, 1, 3, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0],
                                'retweet_count': [3, 0, 2, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                'like_count': [8, 8, 3, 1, 8, 2, 2, 3, 0, 2, 1, 1, 3, 0, 0, 0, 0, 0],
                                'influencer_flag': [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
                                'num_followers': [14019, 722, 261, 1466, 12507, 3, 18551, 161, 17942, 3725, 
                                                6124, 5456, 1859, 319, 3451, 779, 6, 20],
                                'score': [3.1220, 1.6288, 1.6125, 1.3749, 1.3646, 1.2716, 1.0903, 1.0810, 0.9881,
                                        0.9857, 0.9681, 0.9605, 0.7404, 0.7256, 0.6307, 0.5337, 0.4667, 0.2952]})
    
    assert(actual_df.equals(expected_df))