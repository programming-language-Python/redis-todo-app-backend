from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CategoryORM(Base):
    """Модель категории в БД"""

    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
