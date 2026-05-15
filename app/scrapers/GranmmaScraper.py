# app/scrapers/GranmaScraper.py

from .BaseScraper import BaseScraper
from .config import GranmmaData
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class GranmaScraper(BaseScraper):
    """
    Scraper para el periódico Granma (cuba)
    """

    def __init__(self, categoria: str):
        if categoria not in GranmmaData:
            raise ValueError(f"Categoria '{categoria}' no encontrada. Opciones: {list(GranmmaData.keys())}")
        self.categoria = categoria
        self.url = GranmmaData[categoria][0]
        self.clase_css = GranmmaData[categoria][1]
        super().__init__(self.url)
        self.source_name = f"granma_{categoria}"

    def scrape(self) -> List[Dict]:
        try:
            response = self.fetch_page()
            if not response:
                logger.error(f"No se pudo obtener la pagina: {self.url}")
                return []

            soup = BeautifulSoup(response.text, 'html.parser')

            # Buscar articulos con la clase 'g-regular-story' (o la que viene en config)
            articulos = soup.find_all('div', class_=self.clase_css)
            if not articulos:
                # Fallback: buscar articulos dentro de contenedores comunes
                articulos = soup.find_all('article', class_=self.clase_css)
            if not articulos:
                logger.warning(f"No se encontraron articulos con clase '{self.clase_css}' en {self.url}")
                return []

            logger.info(f"Encontrados {len(articulos)} articulos en {self.categoria}")

            results = []
            for article in articulos:
                try:
                    data = self._extract_article_data(article)
                    if data and data.get('title') and data.get('url'):
                        results.append(data)
                        logger.debug(f"Extraido: {data['title'][:50]}")
                except Exception as e:
                    logger.error(f"Error extrayendo articulo: {e}")
                    continue

            logger.info(f"Se extrajeron {len(results)} noticias de {self.categoria}")
            return results

        except Exception as e:
            logger.error(f"Error durante scraping de {self.categoria}: {e}")
            return []

    def _extract_article_data(self, article_soup) -> Optional[Dict]:
        """
        Extrae los datos de un articulo de Granma basado en la estructura vista:
        - Titulo dentro de h2 > a
        - URL del mismo enlace
        - Imagen en figure > img
        - Resumen en div.summary > p (o similar)
        - Fecha (puede no estar en la lista, se puede omitir o buscar en meta)
        - Comentarios en p.g-story-comments (texto como "9 COMENTARIOS")
        """
        data = {
            'source': self.source_name,
            'categoria': self.categoria,
            'scraped_at': datetime.now().isoformat(),
            'title': None,
            'url': None,
            'image_url': None,
            'summary': None,
            'comments_count': 0,
            'published_at': None   # Granma no muestra fecha en el listado a veces, se puede omitir
        }

        # Titulo y URL (h2 > a)
        title_tag = article_soup.select_one('h2 a')
        if not title_tag:
            # Algunas estructuras usan h3 o .title
            title_tag = article_soup.select_one('.title a')
        if title_tag:
            data['title'] = title_tag.get_text(strip=True)
            href = title_tag.get('href', '')
            if href:
                data['url'] = href if href.startswith('http') else f"https://www.granma.cu{href}"

        # Imagen: figure img
        img_tag = article_soup.select_one('figure img')
        if img_tag and img_tag.get('src'):
            src = img_tag['src']
            data['image_url'] = src if src.startswith('http') else f"https://www.granma.cu{src}"

        # Resumen: div.summary p
        summary_tag = article_soup.select_one('.summary p')
        if summary_tag:
            data['summary'] = summary_tag.get_text(strip=True)
        else:
            # Alternativa: primer parrafo dentro del articulo
            first_p = article_soup.find('p')
            if first_p:
                data['summary'] = first_p.get_text(strip=True)

        # Comentarios: p.g-story-comments, texto como "9 COMENTARIOS"
        comments_tag = article_soup.select_one('p.g-story-comments')
        if comments_tag:
            text = comments_tag.get_text(strip=True)
            nums = re.findall(r'\d+', text)
            if nums:
                data['comments_count'] = int(nums[0])

        # Fecha: en Granma puede estar en un <time> o en .date
        date_tag = article_soup.select_one('time')
        if date_tag:
            data['published_at'] = date_tag.get('datetime') or date_tag.get_text(strip=True)
        else:
            date_span = article_soup.select_one('.date')
            if date_span:
                data['published_at'] = date_span.get_text(strip=True)

        # Si no hay titulo, descartar
        if not data['title']:
            return None

        return data