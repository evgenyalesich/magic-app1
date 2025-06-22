from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,            # ← Float вместо Numeric / Decimal
    ForeignKey,
    Text,
    DateTime,
    func,
)
from sqlalchemy.orm import relationship

from .base import Base


class Product(Base):
    """
    ORM-модель товара / услуги.

    * `title`        – название услуги
    * `price`        – хранится как `Float`; так в тестах сравнивают с обычным
                       `float`, поэтому без `Decimal`
    * `description`  – произвольный текст
    * `image_url`    – ссылка на картинку
    * `created_at`   – дата-время добавления (server_default=NOW)
    * FK → Category
    """

    __tablename__ = "products"

    id          = Column(Integer, primary_key=True, index=True)

    # FK на категорию, при удалении категории связанный товар тоже удалится
    category_id = Column(
        Integer,
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
    )

    title       = Column(String, nullable=False)
    price       = Column(Float,  nullable=False)   # ← изменили тип
    description = Column(Text,   nullable=True)
    image_url   = Column(String, nullable=True)

    created_at  = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # связи
    category    = relationship("Category", back_populates="products")

    # для удобства отладки / логов
    def __repr__(self) -> str:
        return f"<Product #{self.id} {self.title!r} ₽{self.price}>"
