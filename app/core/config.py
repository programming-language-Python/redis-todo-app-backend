from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str
    redis_url: str
    cache_ttl_seconds: int
    cache_tasks_key: str
    cors_origins: list[str]


def get_settings() -> Settings:
    return Settings(
        database_url="postgresql+psycopg://postgres:admin@127.0.0.1:5433/postgres",
        redis_url="redis://localhost:6379/0",
        cache_ttl_seconds=3600,  # 1 час базовое нормальное значение
        cache_tasks_key="cache:tasks_list",
        cors_origins=["http://localhost:3000"]
    )
