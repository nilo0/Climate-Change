COLUMNS = [
    'id',
    'username',
    'created_at',
    'name',
    'protected',
    'verified',
    'followers_count',
    'following_count',
    'tweet_count',
    'listed_count',
    'url',
    'description',
]


class User:

    def __init__(self, user):
        self.id = user['id'] if 'id' in user else ""
        self.username = user['username'] if 'username' in user else ""
        self.created_at = user['created_at'] if 'created_at' in user else ""
        self.name = user['name'] if 'name' in user else ""
        self.protected = user['protected'] if 'protected' in user else ""
        self.verified = user['verified'] if 'verified' in user else ""
        self.followers_count = user['public_metrics']['followers_count'] if 'public_metrics' in user and 'followers_count' in user['public_metrics'] else ""
        self.following_count = user['public_metrics']['following_count'] if 'public_metrics' in user and 'following_count' in user['public_metrics'] else ""
        self.tweet_count = user['public_metrics']['tweet_count'] if 'public_metrics' in user and 'tweet_count' in user['public_metrics'] else ""
        self.listed_count = user['public_metrics']['listed_count'] if 'public_metrics' in user and 'listed_count' in user['public_metrics'] else ""
        self.url = user['url'] if 'url' in user else ""
        self.description = user['description'].replace("\n", "") if 'description' in user else ""

    def to_list(self):
        return [
            self.id,
            self.username,
            self.created_at,
            self.name,
            self.protected,
            self.verified,
            self.followers_count,
            self.following_count,
            self.tweet_count,
            self.listed_count,
            self.url,
            self.description,
        ]
