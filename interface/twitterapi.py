import os

import twitter


def post_tweet(status_update):
    api = twitter.Api(consumer_key=os.getenv('TWITTER_CONSUMER_API_KEY'),
                      consumer_secret=os.getenv('TWITTER_CONSUMER_API_SECRET_KEY'),
                      access_token_key=os.getenv('TWITTER_ACCESS_TOKEN'),
                      access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET'))
    return api.PostUpdate(status_update)
