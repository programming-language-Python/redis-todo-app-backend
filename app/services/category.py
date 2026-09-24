from time import perf_counter

from sqlalchemy.orm import Session

from app.cache.redis import RedisCacheBackend
from app.core.config import get_settings
from app.repositories.category import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate

settings = get_settings()


class CategoryNotFoundError(Exception):
    pass


class CategoryService:
    """Ключевые операции с категориями, включая бизнес-логику, валидацию и прочее"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = CategoryRepository(db)
        self.cache = RedisCacheBackend(settings.redis_url, settings.cache_ttl_seconds)

    def list_categories(self) -> list[CategoryRead]:
        start_time = perf_counter()

        cached_categories = self.cache.get(settings.cache_categories_key)
        if cached_categories is not None:
            print(f"Получение списка категорий по кешу заняло {perf_counter() - start_time}")
            return cached_categories

        categories = self.repository.get_all()
        category_read = [CategoryRead.model_validate(category) for category in categories]
        categories_for_cache = [category.model_dump() for category in category_read]
        self.cache.set(settings.cache_categories_key, categories_for_cache)

        print(f"Получение списка категорий заняло {perf_counter() - start_time}")

        return category_read

    def create_category(self, payload: CategoryCreate) -> CategoryRead:
        self.cache.delete(settings.cache_categories_key)

        category = self.repository.create(name=payload.name)
        self.db.commit()
        self.db.refresh(category)
        return CategoryRead.model_validate(category)

    def update_category(self, category_id: str, payload: CategoryUpdate) -> CategoryRead:
        self.cache.delete(settings.cache_categories_key)

        category = self.repository.get_by_id(category_id)
        if category is None:
            raise CategoryNotFoundError

        if payload.name is not None:
            category.name = payload.name

        self.db.commit()
        self.db.refresh(category)
        return CategoryRead.model_validate(category)

    def delete_category(self, category_id: str) -> None:
        self.cache.delete(settings.cache_categories_key)

        category = self.repository.get_by_id(category_id)
        if category is None:
            raise CategoryNotFoundError

        self.repository.delete(category)
        self.db.commit()
