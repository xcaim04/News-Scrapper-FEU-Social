import logging
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
from sqlalchemy import select

from app.config.connect_db import SessionLocal
from app.schemas.models import Article
from app.scrapers.CubadebateScraper import CubadebateScraper
from app.scrapers.GranmmaScraper import GranmaScraper
from app.scrapers.config import GranmmaData, dataNews

logging.basicConfig(level=logging.INFO)


def _parse_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            pass
    return datetime.utcnow()


def _save_article(session: Any, item: Dict) -> bool:
    url = item.get("url")
    if not url:
        return False

    statement = select(Article).where(Article.url == url)
    existing = session.execute(statement).scalar_one_or_none()

    if existing:
        existing.title = item.get("title", existing.title)
        existing.summary = item.get("summary", existing.summary)
        existing.image_url = item.get("image_url", existing.image_url)
        existing.published_at = item.get("published_at", existing.published_at)
        existing.scraped_at = _parse_datetime(item.get("scraped_at"))
        existing.comments_count = item.get(
            "comments_count", existing.comments_count or 0
        )
        existing.categorias = item.get("categorias", existing.categorias)
        existing.source = item.get("source", existing.source)
        existing.categoria = item.get("categoria", existing.categoria)
        existing.clase_css = item.get("clase_css", existing.clase_css)
        return False

    article = Article(
        source=item.get("source", "unknown"),
        categoria=item.get("categoria", "unknown"),
        clase_css=item.get("clase_css"),
        title=item.get("title", "Sin título"),
        url=url,
        summary=item.get("summary"),
        image_url=item.get("image_url"),
        published_at=item.get("published_at"),
        scraped_at=_parse_datetime(item.get("scraped_at")),
        comments_count=item.get("comments_count", 0),
        categorias=item.get("categorias"),
    )
    session.add(article)
    return True


def _scrape_and_save(scraper, session, source_name: str) -> List[Dict]:
    articles = scraper.scrape()
    saved_count = 0
    for item in articles:
        if _save_article(session, item):
            saved_count += 1
    session.commit()
    print(f"   ✅ Guardados: {saved_count} nuevos artículos de {source_name}")
    return articles


def start_scraper() -> pd.DataFrame:
    todos_articulos = []

    with SessionLocal() as session:
        for categoria in dataNews:
            print(f"\n🔍 Scrapeando Cubadebate: {categoria}")
            print(f"   URL: {dataNews[categoria][0]}")
            print(f"   Clase CSS: {dataNews[categoria][1]}")
            print("-" * 50)

            scraper = CubadebateScraper(categoria)
            articulos = _scrape_and_save(scraper, session, f"Cubadebate/{categoria}")
            todos_articulos.extend(articulos)

        for categoria in GranmmaData:
            print(f"\n🔍 Scrapeando Granma: {categoria}")
            print(f"   URL: {GranmmaData[categoria][0]}")
            print(f"   Clase CSS: {GranmmaData[categoria][1]}")
            print("-" * 50)

            scraper = GranmaScraper(categoria)
            articulos = _scrape_and_save(scraper, session, f"Granma/{categoria}")
            todos_articulos.extend(articulos)

    print(f"\n{'=' * 60}")
    print(f"📊 TOTAL DE ARTÍCULOS EXTRAÍDOS: {len(todos_articulos)}")
    print(f"{'=' * 60}")

    return pd.DataFrame(todos_articulos)
