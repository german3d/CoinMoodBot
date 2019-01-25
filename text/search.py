import time
import itertools
import tweepy
from config import CRYPTO_INFO


def _check_twitter_limits(api):
    resource = api.rate_limit_status()["resources"]
    search_status = resource["search"]["/search/tweets"]
    remaining = search_status["remaining"]
    mins_reset = round((search_status["reset"] - time.time()) / 60, 2)
    print(remaining, mins_reset)


def find_subparts(asset):
    """
    Returns keywords of other assets which are parts of compound keywords 
    for current asset.
    """
    output = set()
    keywords_own = CRYPTO_INFO[asset]
    for name, keywords_other in CRYPTO_INFO.items():
        if name==asset:
            continue
        pairs = itertools.product(keywords_own, keywords_other)
        output.update({pair[1] for pair in pairs if pair[1] in pair[0]})
    return output


def make_twitter_query(asset):
    """
    Reurns twitter REST API search query.
    """
    target_tags = CRYPTO_INFO[asset]
    other_dict = {k:v for k,v in CRYPTO_INFO.items() if k!=asset}
    other_tags = set(x for item in other_dict.values() for x in item)
    subparts = find_subparts(asset)
    query = "{target} {exclude} -filter:retweets"\
                .format(target=" OR ".join({"\""+x+"\"" for x in target_tags}),
                        exclude=" ".join({"-\""+x+"\"" for x in other_tags-subparts}))
    return query


def get_twitter_cursor(api, asset, **kwargs):
    """
    Returns twitter search API cursor.
    """
    query = make_twitter_query(asset)
    print(query)
    cursor = tweepy.Cursor(method=api.search,
                           q=query,
                           lang="en",
                           result_type="recent",
                           count=100,
                           include_entities=False,
                           **kwargs
                           )
    return cursor
