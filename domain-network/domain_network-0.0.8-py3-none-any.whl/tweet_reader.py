import pandas as pd
import json

def read_tweets(tweet_dir):
    tweets = []

    for lookup_file in tweet_dir:
        with open(lookup_file, encoding="utf-8") as f:
            for line in f:
                tweet = json.loads(line)
                d = {
                    "id": tweet["id"],
                    "text": tweet["text"],
                    "created_at": tweet["created_at"],
                    "user_name": tweet["user"]["screen_name"],
                    "id_str": tweet["id_str"],
                    "urls": tweet["entities"]["urls"]
                }
                tweets.append(d)

    concatenated_df = pd.DataFrame(tweets)
    concatenated_df = _specify_tweets_with_urls(concatenated_df)
    
    return concatenated_df

def wide_to_long_url (df_tweets):
    long_urls_list = []

    for index, tweet in df_tweets.iterrows():
        for url in tweet['urls']:
            tweet_url = {
                'id': tweet['id'],
                'created_at': tweet['created_at'],
                'url': url['url'],
                'expanded_url': url['expanded_url'],
                'user_name': tweet['user_name']
            }
            long_urls_list.append(tweet_url)

    df_long_urls = pd.DataFrame(long_urls_list)
    return df_long_urls

def _specify_tweets_with_urls (df):
    df['urls'] = df['urls'].apply(lambda x: list(x))
    df['has_url'] = df['urls'].apply(lambda x: 'yes' if len(x) > 0 else 'no')
    return df

