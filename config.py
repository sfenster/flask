import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    pass

class ProductionConfig(Config):
    REDISHOST = "containers-us-west-21.railway.app"
    REDISPASSWORD = "2gx4RQQxAefIetwlDnM8"
    REDISPORT = 5649
    REDISUSER = "default"
    REDISURL = "redis://${{ REDISUSER }}:${{ REDISPASSWORD }}@${{ REDISHOST }}:${{ REDISPORT }}"

class StagingConfig(Config):
    DEBUG = True
    REDISHOST = "containers-us-west-32.railway.app"
    REDISPASSWORD = "mUbNwvKUMpSHTHGjLLpt"
    REDISPORT = 7433
    REDISUSER = "default"
    REDISURL = "redis://${{ REDISUSER }}:${{ REDISPASSWORD }}@${{ REDISHOST }}:${{ REDISPORT }}"


class DevelopmentConfig(Config):
    DEBUG = True
    REDISURL = "redis://localhost:6379"
