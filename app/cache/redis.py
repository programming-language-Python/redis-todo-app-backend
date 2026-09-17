import json

from redis import Redis


class RedisCacheBackend:
    def __init__(self, redis_url: str, cache_ttl_seconds: int | None = None):
        # по умолчанию в Redis данные передаются в байтах, чтоб их декодировать в строку используется decoded_response=True
        self.redis = Redis.from_url(redis_url, decode_responses=True)
        self.cache_ttl_seconds = cache_ttl_seconds

    def set(self, key: str, value: dict) -> None:
        # json.dumps -  преобразует json в python объект
        self.redis.set(key, json.dumps(value), ex=self.cache_ttl_seconds)

    def get(self, key: str) -> dict:
        # json.loads - преобразует json-строку в dict
        value = self.redis.get(key)
        if value is not None:
            return json.loads(value)

    def delete(self, key: str) -> None:
        # можно удалить несколько ключей:
        # self.redis.delete(*keys)
        self.redis.delete(key)
