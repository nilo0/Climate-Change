COLUMNS = [
    'id',
    'author_id',
    'conversation_id',
    'created_at',
    'lang',
    'retweet_count',
    'reply_count',
    'like_count',
    'quote_count',
    'reply_settings',
    'text',
]


class Tweet:

    def __init__(self, tweet):
        self.id = tweet['id'] if 'id' in tweet else ""
        self.author_id = tweet['author_id'] if 'author_id' in tweet else ""
        self.conversation_id = tweet['conversation_id'] if 'conversation_id' in tweet else ""
        self.created_at = tweet['created_at'] if 'created_at' in tweet else ""
        self.lang = tweet['lang'] if 'lang' in tweet else ""
        self.retweet_count = tweet['public_metrics']['retweet_count'] if 'public_metrics' in tweet and 'retweet_count' in tweet['public_metrics'] else ""
        self.reply_count = tweet['public_metrics']['reply_count'] if 'public_metrics' in tweet and 'reply_count' in tweet['public_metrics'] else ""
        self.like_count = tweet['public_metrics']['like_count'] if 'public_metrics' in tweet and 'like_count' in tweet['public_metrics'] else ""
        self.quote_count = tweet['public_metrics']['quote_count'] if 'public_metrics' in tweet and 'quote_count' in tweet['public_metrics'] else ""
        self.reply_settings = tweet['reply_settings'] if 'reply_settings' in tweet else ""
        self.text = tweet['text'].replace("\n", "") if 'text' in tweet else ""

    def to_list(self):
        return [
            self.id,
            self.author_id,
            self.conversation_id,
            self.created_at,
            self.lang,
            self.retweet_count,
            self.reply_count,
            self.like_count,
            self.quote_count,
            self.reply_settings,
            self.text,
        ]
