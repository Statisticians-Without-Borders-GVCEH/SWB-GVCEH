import pickle

import pandas as pd

SUB_QUERY_CHUNKS = 17  ### how many queries we split Appendix C + E + D into
NEIGHBOURHOOD_CHUNKS = 10  ### split neighbourhood into how many chunks ?
NUM_ACCOUNTS_TO_TARGET = 5  ### How many queries we split Appendix B into

QUERY_MAX_LENGTH = 512

MAX_PER_15 = 9999  ### TODO: Find this limit
QUERY_CACHE_FILE = "querylist.pkl"


def load_keywords():
    """
    Loads our appendices into a dict of lists:
    returns: {
        'ac': [],
        'ad': [],
        'ae': []
    }
    """
    data = pd.read_csv("../appendices/ac.csv", index_col=0)
    kw1 = [k.strip().lower() for k in data.Organizations.tolist()]

    data = pd.read_csv("../appendices/ad.csv", index_col=0)
    kw2 = [k.strip().lower() for k in data.sectors.tolist()]

    data = pd.read_csv("../appendices/ae.csv", index_col=0)
    kw3 = [k.strip().lower() for k in data.word.tolist()]

    return {"ac": kw1, "ad": kw2, "ae": kw3}


def prep_subq(KEYWORDS_DICT, CHUNKS):
    """
    Generates the list of strings
    Each string is the keyword subquery
    """
    ### make one list of keywords
    if type(KEYWORDS_DICT) is not list:
        allkw = sum(KEYWORDS_DICT.values(), [])
    else:
        allkw = KEYWORDS_DICT

    ### chunk it down, we can't exceed 512 character a query
    allkw = [allkw[i::CHUNKS] for i in range(CHUNKS)]

    subq = []

    for a in allkw:
        ### we use OR to help reduce number of queries
        subq.append(" OR ".join(a))

    return subq


def gen_query_one(SUB_QUERY):
    """
    Generates a list of queries containing neighbourhood x keyword products
    """

    ### get our neighbourhoods
    data = pd.read_csv("../appendices/aa_old.csv", index_col=0)

    neighbourhoods = [n.strip().lower() for n in data.Location.tolist()]

    neighbourhoods = prep_subq(neighbourhoods, NEIGHBOURHOOD_CHUNKS)

    ### now to make our queries with the neighbourhoods
    query1 = []

    for n in neighbourhoods:
        for kws in SUB_QUERY:
            querytext = f"({n}) ({kws}) lang:en -is:retweet"
            if len(querytext) > QUERY_MAX_LENGTH:
                print("WARNING: QUERY 1 TOO LARGE")
                print("CHUNK KEYWORD UNION SMALLER")
            # max = len(querytext) if len(querytext) > max else max
            query1.append((querytext, n))

    # print(max)

    ### returing a list of queries from this product
    return query1


def gen_query_two(SUB_QUERY):
    """
    Generate list of CRD identifies x keywords
    """

    ### our CRD level keywords
    neighbourhoods = [
        "Greater Victoria",
        "#GreaterVictoria",
        "Victoria",
        "VictoriaBC",
        "Victoria B.C.",
        "#YYJ",
        "YYJ",
        "#GVCEH",
        "Greater Victoria Coalition to End Homelessness",
    ]

    ### now to make our queries with the neighbourhoods
    query = []

    for n in neighbourhoods:
        for kws in SUB_QUERY:
            querytext = f"{n} ({kws}) lang:en -is:retweet"
            if len(querytext) > QUERY_MAX_LENGTH:
                print("WARNING: QUERY 2 TOO LARGE")
                print("CHUNK KEYWORD UNION SMALLER")
                print(querytext)
                print(len(querytext))
            query.append((querytext, n))

    ### returing a list of queries from this product
    return query


def chunker(seq, size):
    return (seq[pos : pos + size] for pos in range(0, len(seq), size))


def gen_query_three(SUB_QUERY):
    """
    Check specific twitter accounts for tweets
    """

    ### load the names from the appendix
    data = pd.read_csv("../appendices/aborganizations.csv", index_col=0)

    orgs = [n.strip().lower() for n in data.Organizations.tolist()]

    data = pd.read_csv("../appendices/abpersons.csv", index_col=0)

    pers = [n.strip().lower() for n in data.Influencers.tolist()]

    ### loop through like above to generate queries
    query = []

    for grp in chunker(orgs + pers, NUM_ACCOUNTS_TO_TARGET):

        subtext = []
        for name in grp:
            subtext.append(f"from:{name}")

        subtext = " OR ".join(subtext)

        for kws in SUB_QUERY:
            querytext = f"({subtext}) ({kws}) lang:en -is:retweet"
            if len(querytext) > QUERY_MAX_LENGTH:
                print("WARNING: QUERY 3 TOO LARGE")
                print("CHUNK KEYWORD UNION SMALLER")
                print(querytext)
                print(len(querytext))
            query.append((querytext, "individual"))

    return query


def gen_queries():
    # load keywords
    keywords = load_keywords()

    ### generate query keyword paramteres
    ### prep keyword union
    subq = prep_subq(keywords, SUB_QUERY_CHUNKS)

    # query 1 - neighbourhood keyword products
    print("Generating Query 1...")
    q1 = gen_query_one(subq)

    # query 2 - CRD keyword products
    print("Generating Query 2...")
    q2 = gen_query_two(subq)

    # query 3 - account keyword products
    print("Generating Query 3")
    q3 = gen_query_three(subq)

    # query 4 - geotagged tweets
    q4 = []

    ### combine
    queries = q1 + q2 + q3 + q4

    print(f"Total # of queries: {len(queries)}")
    # print(f"Will take {len(queries) / MAX_PER_15} attempts")
    print(f"Will take minimum {(len(queries)*2.1)/60} minutes")

    # cache queries
    print("Writing...")
    with open(QUERY_CACHE_FILE, "wb") as f:
        pickle.dump(queries, f)


if __name__ == "__main__":
    ### gen_queries
    gen_queries()
