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
    'referenced_tweets',
    'text',
]

class Quote:

    def __init__(self, quote):
        self.id = quote['id'] if 'id' in quote else ""
        self.author_id = quote['author_id'] if 'author_id' in quote else ""
        self.conversation_id = quote['conversation_id'] if 'conversation_id' in quote else ""
        self.created_at = quote['created_at'] if 'created_at' in quote else ""
        self.lang = quote['lang'] if 'lang' in quote else ""
        self.retweet_count = quote['public_metrics']['retweet_count'] if 'public_metrics' in quote and 'retweet_count' in quote['public_metrics'] else ""
        self.reply_count = quote['public_metrics']['reply_count'] if 'public_metrics' in quote and 'reply_count' in quote['public_metrics'] else ""
        self.like_count = quote['public_metrics']['like_count'] if 'public_metrics' in quote and 'like_count' in quote['public_metrics'] else ""
        self.quote_count = quote['public_metrics']['quote_count'] if 'public_metrics' in quote and 'quote_count' in quote['public_metrics'] else ""
        self.referenced_tweets = quote['referenced_tweets'] if 'referenced_tweets' in quote else ""
        self.text = quote['text'].replace("\n", "") if 'text' in quote else ""

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
            self.referenced_tweets,
            self.text,
        ]
