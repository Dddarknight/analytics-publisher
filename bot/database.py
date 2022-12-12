import redis


def init_db():
    return redis.Redis(db=2)
