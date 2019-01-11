import mongoengine


class History(mongoengine.Document):
    username = mongoengine.StringField(required=True, unique=True)
    insta_username = mongoengine.StringField(required=True, unique=True)
    clicked_links = mongoengine.ListField()
    accounts_counter = mongoengine.ListField()


class Users(mongoengine.Document):
    username = mongoengine.StringField(required=True, unique=True)
    email_address = mongoengine.EmailField(required=True)
    insta_username = mongoengine.StringField(required=True, unique=True)


class Metrics(mongoengine.Document):
    username = mongoengine.StringField(required=True)
    insta_username = mongoengine.StringField(required=True)
    datetime = mongoengine.DateTimeField(required=True, unique=True)
    Sleeptime = mongoengine.FloatField()
    Connection = mongoengine.IntField()
    Links_opened = mongoengine.IntField()
    New_post_opened = mongoengine.IntField()
    Post_liked = mongoengine.IntField()
    Post_not_liked = mongoengine.IntField()
    execution_time = mongoengine.FloatField()


# class Time(mongoengine.EmbeddedDocument):
#     timeout = mongoengine.IntField(min_value=10, max_value=30)
#     delay_min = mongoengine.IntField(required=True)
#     delay_max = mongoengine.IntField(required=True)
#
#
# class Limits(mongoengine.EmbeddedDocument):
#     posts_per_hashtage_min = mongoengine.IntField(min_value=1, required=True)
#     posts_per_hashtage_max = mongoengine.IntField(min_value=1, required=True)
#     total_likes_max = mongoengine.IntField(min_value=1, required=True)


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
