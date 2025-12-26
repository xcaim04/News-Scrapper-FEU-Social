import requests
from bs4 import BeautifulSoup

class BaseScraper:
    """
    Clase base para scrapers web.
    Define la estructura general: fetch_html, parse_html y run.
    Las clases hijas deben implementar extract_data.
    """

    def __init__(self, url):
        self.url = url
        self.html = None
        self.soup = None

    def fetch_html(self):
        """Descarga el HTML desde la URL"""
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }
        response = requests.get(self.url, headers=headers)
        if response.status_code == 200:
            self.html = response.text
        else:
            raise Exception(f"Error al obtener la página: {response.status_code}")

    def parse_html(self):
        """Convierte el HTML en un objeto BeautifulSoup"""
        if self.html:
            self.soup = BeautifulSoup(self.html, "html.parser")
        else:
            raise Exception("No hay HTML para parsear. Ejecuta fetch_html primero.")

    def extract_data(self):
        """
        Método abstracto: debe ser implementado por las clases hijas.
        Debe devolver la información relevante del sitio.
        """
        raise NotImplementedError("Debes implementar extract_data en la clase hija.")

    def run(self):
        """Ejecuta todo el flujo"""
        self.fetch_html()
        self.parse_html()
        return self.extract_data()
