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


class Reply:

    def __init__(self, reply):
        self.id = reply['id'] if 'id' in reply else ""
        self.author_id = reply['author_id'] if 'author_id' in reply else ""
        self.conversation_id = reply['conversation_id'] if 'conversation_id' in reply else ""
        self.created_at = reply['created_at'] if 'created_at' in reply else ""
        self.lang = reply['lang'] if 'lang' in reply else ""
        self.retweet_count = reply['public_metrics']['retweet_count'] if 'public_metrics' in reply and 'retweet_count' in reply['public_metrics'] else ""
        self.reply_count = reply['public_metrics']['reply_count'] if 'public_metrics' in reply and 'reply_count' in reply['public_metrics'] else ""
        self.like_count = reply['public_metrics']['like_count'] if 'public_metrics' in reply and 'like_count' in reply['public_metrics'] else ""
        self.quote_count = reply['public_metrics']['quote_count'] if 'public_metrics' in reply and 'quote_count' in reply['public_metrics'] else ""
        self.referenced_tweets = reply['referenced_tweets'] if 'referenced_tweets' in reply else ""
        self.text = reply['text'].replace("\n", "") if 'text' in reply else ""

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
