from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, JSON, String, Text

from app.config.connect_db import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(150), nullable=False)
    categoria = Column(String(150), nullable=False)
    clase_css = Column(String(150), nullable=True)
    title = Column(String(1000), nullable=False)
    url = Column(String(1500), nullable=False, unique=True, index=True)
    summary = Column(Text, nullable=True)
    image_url = Column(String(1500), nullable=True)
    published_at = Column(String(150), nullable=True)
    scraped_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    comments_count = Column(Integer, nullable=True, default=0)
    categorias = Column(JSON, nullable=True)
