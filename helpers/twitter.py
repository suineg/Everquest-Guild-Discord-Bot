import os

import twitter


def post_tweet(status_update):
    api = twitter.Api(consumer_key=os.environ['TWITTER_CONSUMER_API_KEY'],
                      consumer_secret=os.environ['TWITTER_CONSUMER_API_SECRET_KEY'],
                      access_token_key=os.environ['TWITTER_ACCESS_TOKEN'],
                      access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET'])
    try:
        status = api.PostUpdate(status_update)
    except UnicodeDecodeError:
        status = """```
Your message could not be encoded.  Perhaps it contains non-ASCII characters?
Try explicitly specifying the encoding with the --encoding flag
```"""
    finally:
        return status
