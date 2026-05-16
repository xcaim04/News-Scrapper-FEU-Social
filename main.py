# main.py

from app.scrapers.CubadebateScraper import CubadebateScraper
from app.scrapers.config import dataNews
import pandas as pd
from datetime import datetime
import os
import logging

logging.basicConfig(level=logging.INFO)


def main():
    # Lista de categorías a scrapear (todas o las que quieras)
    categorias = list(dataNews.keys())

    # O puedes seleccionar solo algunas
    # categorias = ["politica", "economia", "militar y inteligencia"]

    todos_articulos = []

    for categoria in categorias:
        print(f"\n🔍 Scrapeando: {categoria}")
        print(f"   URL: {dataNews[categoria][0]}")
        print(f"   Clase CSS: {dataNews[categoria][1]}")
        print("-" * 50)

        scraper = CubadebateScraper(categoria)
        articulos = scraper.scrape()

        print(f"   ✅ Encontrados: {len(articulos)} artículos")
        todos_articulos.extend(articulos)

    print(f"\n{'=' * 60}")
    print(f"📊 TOTAL DE ARTÍCULOS EXTRAÍDOS: {len(todos_articulos)}")
    print(f"{'=' * 60}")

    df = pd.DataFrame(todos_articulos)
    os.makedirs("exports", exist_ok=True)
    df.to_csv("exports/cubadebate_articulos.csv", index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    main()
