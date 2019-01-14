import mongoengine


class History(mongoengine.Document):
    username = mongoengine.StringField(required=True, unique=True)
    insta_username = mongoengine.StringField(required=True, unique=True)
    clicked_links = mongoengine.ListField()
    accounts_counter = mongoengine.ListField()


class Users(mongoengine.Document):
    username = mongoengine.StringField(required=True, unique=True)
    email_address = mongoengine.EmailField(required=True)
    password = mongoengine.StringField(required=True)


class Accounts(mongoengine.Document):
    username = mongoengine.StringField(required=True, unique=True)
    insta_username = mongoengine.StringField(required=True, unique=True)
    insta_password = mongoengine.StringField(required=True)


class Metrics(mongoengine.Document):
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


class Rules(mongoengine.Document):
    username = mongoengine.StringField(required=True, unique=True)
    insta_username = mongoengine.StringField(required=True, unique=True)
    general = mongoengine.DictField(required=True)
    connection = mongoengine.DictField(required=True)
    get_followers = mongoengine.DictField(required=True)
    like = mongoengine.DictField(required=True)


class UserInputs(mongoengine.Document):
    username = mongoengine.StringField(required=True, unique=True)
    insta_username = mongoengine.StringField(required=True, unique=True)
    hashtags = mongoengine.ListField()
