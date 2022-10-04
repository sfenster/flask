import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    pass

class ProductionConfig(Config):
    pass

class StagingConfig(Config):
    DEBUG = True

class DevelopmentConfig(Config):
    DEBUG = True
