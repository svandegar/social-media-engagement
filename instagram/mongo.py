import mongoengine

""" MongoDb document classes """


class History(mongoengine.DynamicDocument):
    username = mongoengine.StringField(required=True)
    insta_username = mongoengine.StringField(required=True, unique=True)
    clicked_links = mongoengine.ListField()
    accounts_counter = mongoengine.ListField()


class Users(mongoengine.DynamicDocument):
    username = mongoengine.StringField(required=True, unique=True)
    email_address = mongoengine.EmailField(required=True)
    password = mongoengine.StringField(required=True)
    use_proxy = mongoengine.BooleanField(False)


class Accounts(mongoengine.DynamicDocument):
    username = mongoengine.StringField(required=True)
    insta_username = mongoengine.StringField(required=True, unique=True)
    insta_password = mongoengine.StringField(required=True)


class Metrics(mongoengine.DynamicDocument):
    username = mongoengine.StringField(required=True)
    insta_username = mongoengine.StringField(required=True)
    datetime = mongoengine.DateTimeField(required=True, unique=True)
    sleeptime = mongoengine.FloatField()
    connection = mongoengine.IntField()
    links_opened = mongoengine.IntField()
    new_post_opened = mongoengine.IntField()
    post_liked = mongoengine.IntField()
    post_not_liked = mongoengine.IntField()
    execution_time = mongoengine.FloatField()
    followers = mongoengine.IntField()


class Rules(mongoengine.DynamicDocument):
    username = mongoengine.StringField(required=True)
    insta_username = mongoengine.StringField(required=True, unique=True)
    general = mongoengine.DictField(required=True)
    connection = mongoengine.DictField(required=True)
    get_followers = mongoengine.DictField(required=True)
    like = mongoengine.DictField(required=True)


class UserInputs(mongoengine.DynamicDocument):
    username = mongoengine.StringField(required=True)
    insta_username = mongoengine.StringField(required=True, unique=True)
    hashtags = mongoengine.ListField()


class Followers(mongoengine.DynamicDocument):
    account = mongoengine.StringField(required=True)
    date = mongoengine.DateField(required=True, unique=False)
    followers = mongoengine.ListField(required=False)
    followers_count = mongoengine.IntField(required=False)
    new_followers = mongoengine.ListField(required=False)
    new_followers_count = mongoengine.IntField(required=False)


class Proxies(mongoengine.DynamicDocument):
    location = mongoengine.StringField(required= True, unique=True)
    shared = mongoengine.BooleanField(required = True)
    username = mongoengine.StringField(required=True)
    proxy = mongoengine.DictField(required=True,unique=True)


class Schedules(mongoengine.DynamicDocument):
    username = mongoengine.StringField(required=True)
    insta_username = mongoengine.StringField(required=True, unique=True)
    schedule_activated = mongoengine.BooleanField(default=False)
    schedules = mongoengine.ListField(required=False)
