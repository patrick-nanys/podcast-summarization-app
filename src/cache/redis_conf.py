"""Configuration file for redis"""
import os
import redis
from redis import asyncio as Redis
from utils import conf_helper

config = conf_helper.read_configuration()

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/1")
# redis = Redis(host=config['redisSettings']['host'], port=config['redisSettings']['port'], db=1) # authx implementation
redis_client = redis.Redis.from_url(REDIS_URL)
