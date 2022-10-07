import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

class ProductionConfig(Config):
    REDISURL = os.getenv('REDIS_URL')

class StagingConfig(Config):
    DEBUG = True
    REDISURL = os.getenv('REDIS_URL')


class DevelopmentConfig(Config):
    DEBUG = True
    REDISURL = "redis://localhost:6379"
