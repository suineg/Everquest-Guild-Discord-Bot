import os
from collections import namedtuple

import twitter

Status = namedtuple('Status', ['id',
                               'text'])


def post_tweet(status_update):
    status = None
    api = twitter.Api(consumer_key=os.getenv('TWITTER_CONSUMER_API_KEY', 0),
                      consumer_secret=os.getenv('TWITTER_CONSUMER_API_SECRET_KEY', 0),
                      access_token_key=os.getenv('TWITTER_ACCESS_TOKEN', 0),
                      access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET', 0))
    try:
        status = api.PostUpdate(status_update)
    except UnicodeDecodeError:
        status = """```
Your message could not be encoded.  Perhaps it contains non-ASCII characters?
Try explicitly specifying the encoding with the --encoding flag
```"""
    except Exception as e:
        status = Status(id=0, text='This was a test')
        print(status)
        print(e.with_traceback())
    finally:
        return status
