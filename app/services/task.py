from time import perf_counter

from sqlalchemy.orm import Session

from app.cache.redis import RedisCacheBackend
from app.core.config import get_settings
from app.repositories.task import TaskRepository
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate

settings = get_settings()


class TaskNotFoundError(Exception):
    pass


class TaskService:
    """Ключевые операции с задачами, включая бизнес-логику, валидацию и прочее"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = TaskRepository(db)
        self.cache = RedisCacheBackend(settings.redis_url, settings.cache_ttl_seconds)

    def list_tasks(self) -> list[TaskRead]:
        start_time = perf_counter()

        # Добавить шаг 1: проверить есть ли данные в Redis
        cached_tasks = self.cache.get(settings.cache_tasks_key)
        if cached_tasks is not None:
            print(f"Получение списка задач по кешу заняло {perf_counter() - start_time}")
            return cached_tasks

        tasks = self.repository.get_all()  # шаг 2 по схеме (идём в БД, если в кеше данных нет)

        # Добавить шаг 3: Сохранить в кеш, если данные в кеше нет
        task_read = [TaskRead.model_validate(task) for task in tasks]
        tasks_for_cache = [task.model_dump() for task in task_read]
        self.cache.set(settings.cache_tasks_key, tasks_for_cache)

        print(f"Получение списка задач заняло {perf_counter() - start_time}")

        return task_read  # шаг 4

    def create_task(self, payload: TaskCreate) -> TaskRead:
        # шаг 5 Инвалидация кеша (чтоб он был актуальным)
        self.cache.delete(settings.cache_tasks_key)

        task = self.repository.create(title=payload.title)
        self.db.commit()
        self.db.refresh(task)
        return TaskRead.model_validate(task)

    def update_task(self, task_id: str, payload: TaskUpdate) -> TaskRead:
        # шаг 5 Инвалидация кеша (чтоб он был актуальным)
        self.cache.delete(settings.cache_tasks_key)

        task = self.repository.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError

        if payload.title is not None:
            task.title = payload.title
        if payload.completed is not None:
            task.completed = payload.completed

        self.db.commit()
        self.db.refresh(task)
        return TaskRead.model_validate(task)

    def delete_task(self, task_id: str) -> None:
        # шаг 5 Инвалидация кеша (чтоб он был актуальным)
        self.cache.delete(settings.cache_tasks_key)

        task = self.repository.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError

        self.repository.delete(task)
        self.db.commit()
