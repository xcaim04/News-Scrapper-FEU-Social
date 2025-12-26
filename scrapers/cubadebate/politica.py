import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from scrapers.base_scraper import BaseScraper
import requests
from bs4 import BeautifulSoup
import time

class PoliticaScraper(BaseScraper):
    """
    Scraper especializado en la sección de Política de Cubadebate.
    Hereda de BaseScraper y redefine extract_data para obtener titulares,
    enlaces, fecha, imagen, resumen y contenido completo de cada noticia.
    """
    
    def __init__(self, url):
        super().__init__(url)
        self.base_url = "http://www.cubadebate.cu"

    def extract_data(self):
        """Extrae titulares y metadatos de la portada de Política"""
        noticias = []
        for post in self.soup.find_all("div", class_="bigimage_post"):
            categorias = [a.get_text(strip=True) for a in post.find("h3", class_="cat_title").find_all("a")]

            titulo_tag = post.find("div", class_="title").find("a")
            titulo = titulo_tag.get_text(strip=True) if titulo_tag else None
            enlace_relativo = titulo_tag["href"] if titulo_tag else None
            if enlace_relativo and not enlace_relativo.startswith('http'):
                enlace = self.base_url + enlace_relativo
            else:
                enlace = enlace_relativo

            fecha_tag = post.find("time")
            fecha = fecha_tag.get_text(strip=True) if fecha_tag else None
            fecha_iso = fecha_tag["datetime"] if fecha_tag and fecha_tag.has_attr("datetime") else None

            img_tag = post.find("img")
            imagen = img_tag["src"] if img_tag else None

            excerpt_tag = post.find("div", class_="excerpt")
            resumen = excerpt_tag.get_text(strip=True) if excerpt_tag else None

            noticia = {
                "categorias": categorias,
                "titulo": titulo,
                "enlace": enlace,
                "fecha": fecha,
                "fecha_iso": fecha_iso,
                "imagen": imagen,
                "resumen": resumen
            }

            # Enriquecer con contenido completo
            if enlace:
                articulo = self.extract_article(enlace)
                if articulo:
                    noticia.update(articulo)
                time.sleep(1)  # Pausa para no sobrecargar el servidor

            noticias.append(noticia)

        return noticias

    def extract_article(self, enlace):
        """Visita cada enlace y extrae el contenido completo"""
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }
        response = requests.get(enlace, headers=headers)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # Texto principal del artículo
        cuerpo = " ".join([p.get_text(strip=True) for p in soup.find_all("p")])

        # Autor (si existe)
        autor_tag = soup.find("span", class_="author")
        autor = autor_tag.get_text(strip=True) if autor_tag else None

        # Etiquetas o categorías adicionales
        etiquetas = [a.get_text(strip=True) for a in soup.find_all("a", rel="tag")]

        return {
            "cuerpo": cuerpo,
            "autor": autor,
            "etiquetas": etiquetas
        }

scraper = PoliticaScraper("http://www.cubadebate.cu/categoria/temas/politica-temas/")
noticias = scraper.run()

for n in noticias:
    print(n["titulo"])
    print(n["fecha"], n["enlace"])
    print("Autor:", n.get("autor"))
    print("Etiquetas:", n.get("etiquetas"))
    print("Resumen:", n["resumen"])
    print("Contenido:", n["cuerpo"][:200], "...\n")  # mostrar solo inicio del texto
