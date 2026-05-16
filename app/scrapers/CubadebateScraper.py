# app/scrapers/CubadebateScraper.py

from .BaseScraper import BaseScraper
from .config import dataNews, SELECTORES
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class CubadebateScraper(BaseScraper):
    """
    Scraper para Cubadebate usando la estructura dataNews
    """

    def __init__(self, categoria: str):
        """
        Args:
            categoria: Clave de la categoría (politica, economia, etc.)
        """
        if categoria not in dataNews:
            raise ValueError(
                f"Categoría '{categoria}' no encontrada. Opciones: {list(dataNews.keys())}"
            )

        self.categoria = categoria
        self.url = dataNews[categoria][0]  # La URL está en la posición 0
        self.clase_css = dataNews[categoria][1]  # La clase CSS está en la posición 1
        super().__init__(self.url)
        self.source_name = f"cubadebate_{categoria}"

    def scrape(self) -> List[Dict]:
        """
        Extrae todas las noticias de la categoría usando la clase CSS proporcionada
        """
        try:
            response = self.fetch_page()
            if not response:
                logger.error(f"No se pudo obtener la página: {self.url}")
                return []

            soup = BeautifulSoup(response.text, "html.parser")

            # Buscar los divs que tienen la clase CSS específica de la categoría
            # Ej: 'politica-temas', 'economia-temas', 'militar-e-inteligencia', etc.
            clase_buscar = self.clase_css

            # Buscar divs que contengan la clase (puede tener múltiples clases)
            articulos = soup.find_all(
                "div", class_=lambda x: x and clase_buscar in x.split()
            )

            if not articulos:
                # Intentar búsqueda exacta
                articulos = soup.find_all("div", class_=clase_buscar)

            if not articulos:
                # Fallback: buscar divs image_post que contengan la clase en sus clases
                articulos = soup.find_all(
                    "div",
                    class_=lambda x: (
                        x and "image_post" in x.split() and clase_buscar in x.split()
                    ),
                )

            if not articulos:
                logger.warning(
                    f"No se encontraron artículos con clase '{clase_buscar}' en {self.url}"
                )
                # Mostrar las primeras clases encontradas para debug
                all_divs = soup.find_all("div", class_=True)[:5]
                logger.debug(
                    f"Ejemplo de clases encontradas: {[d.get('class') for d in all_divs]}"
                )
                return []

            logger.info(
                f"Encontrados {len(articulos)} artículos con clase '{clase_buscar}'"
            )

            results = []
            for article_div in articulos:
                try:
                    article_data = self._extract_article_data(article_div)
                    if (
                        article_data
                        and article_data.get("title")
                        and article_data.get("url")
                    ):
                        article_data["source"] = self.source_name
                        article_data["categoria"] = self.categoria
                        article_data["clase_css"] = self.clase_css
                        results.append(article_data)
                        logger.debug(f"✓ Extraído: {article_data['title'][:50]}...")
                except Exception as e:
                    logger.error(f"Error extrayendo artículo: {e}")
                    continue

            logger.info(f"=> Se extrajeron {len(results)} noticias de {self.categoria}")
            return results

        except Exception as e:
            logger.error(f"Error durante el scraping de {self.categoria}: {e}")
            return []

    def _extract_article_data(self, article_div) -> Optional[Dict]:
        """
        Extrae los datos de un artículo usando los selectores basados en el HTML real
        """
        data = {"scraped_at": datetime.now().isoformat()}

        # TÍTULO y URL - Están en div.title > a
        title_tag = article_div.select_one("div.title a")
        if title_tag:
            data["title"] = title_tag.get_text(strip=True)
            data["url"] = title_tag.get("href", "")
            if data["url"] and not data["url"].startswith("http"):
                data["url"] = f"http://www.cubadebate.cu{data['url']}"
        else:
            # Fallback: buscar cualquier a que parezca título
            title_tag = article_div.find("a", href=True)
            if title_tag and "/noticias/" in title_tag.get("href", ""):
                data["title"] = title_tag.get_text(strip=True) or "Sin título"
                data["url"] = title_tag.get("href", "")
                if data["url"] and not data["url"].startswith("http"):
                    data["url"] = f"http://www.cubadebate.cu{data['url']}"
            else:
                return None

        # FECHA - Está en tag time
        date_tag = article_div.select_one("time")
        if date_tag:
            data["published_at"] = date_tag.get(
                "datetime", date_tag.get_text(strip=True)
            )

        # RESUMEN - Está en div.excerpt > p
        summary_tag = article_div.select_one("div.excerpt p")
        if summary_tag:
            data["summary"] = summary_tag.get_text(strip=True)

        # IMAGEN - Está en a.left.media > img
        img_tag = article_div.select_one("a.left.media img")
        if img_tag and img_tag.get("src"):
            img_src = img_tag["src"]
            if not img_src.startswith("http"):
                img_src = f"http://media.cubadebate.cu{img_src}"
            data["image_url"] = img_src

        # CATEGORÍAS - Están en h3.cat_title > a
        categories = []
        cat_tags = article_div.select("h3.cat_title a")
        for tag in cat_tags:
            categories.append(tag.get_text(strip=True))
        if categories:
            data["categorias"] = categories

        # COMENTARIOS
        comments_tag = article_div.select_one("span.comment_count a")
        if comments_tag:
            comments_text = comments_tag.get_text(strip=True)
            numbers = re.findall(r"\d+", comments_text)
            if numbers:
                data["comments_count"] = int(numbers[0])
            else:
                data["comments_count"] = 0

        return data


# Función para scrapear múltiples categorías
def scrape_multiple_categorias(categorias: List[str]) -> Dict[str, List[Dict]]:
    resultados = {}
    for categoria in categorias:
        if categoria in dataNews:
            scraper = CubadebateScraper(categoria)
            resultados[categoria] = scraper.scrape()
        else:
            logger.warning(f"Categoría '{categoria}' no existe")
            resultados[categoria] = []
    return resultados
