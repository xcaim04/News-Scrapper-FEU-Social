import requests
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """
    Clase base abstracta para todos los scrapers
    Proporciona funcionalidades comunes como fetching de páginas,
    manejo de errores, reintentos, etc.
    """

    def __init__(self, url: str, timeout: int = 30, max_retries: int = 3):
        """
        Inicializa el scraper base

        Args:
            url: URL del sitio a scrapear
            timeout: Timeout en segundos para las peticiones
            max_retries: Número máximo de reintentos en caso de fallo
        """
        self.url = url
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = self._create_session()

        # Headers por defecto para simular un navegador real
        self.default_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.8,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }

    def _create_session(self) -> requests.Session:
        """
        Crea una sesión de requests con estrategia de reintentos

        Returns:
            requests.Session configurada
        """
        session = requests.Session()

        # Estrategia de reintentos para peticiones fallidas
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,  # Espera 1, 2, 4 segundos entre reintentos
            status_forcelist=[429, 500, 502, 503, 504],  # Códigos HTTP a reintentar
            allowed_methods=["HEAD", "GET", "OPTIONS"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def fetch_page(self, headers: Optional[Dict] = None) -> Optional[requests.Response]:
        """
        Descarga la página HTML con manejo de errores y reintentos

        Args:
            headers: Headers adicionales para la petición (opcional)

        Returns:
            requests.Response si es exitoso, None si falla
        """
        try:
            # Combinar headers por defecto con los proporcionados
            request_headers = self.default_headers.copy()
            if headers:
                request_headers.update(headers)

            logger.debug(f"Fetching: {self.url}")

            response = self.session.get(
                self.url,
                headers=request_headers,
                timeout=self.timeout,
                allow_redirects=True,
            )

            response.raise_for_status()  # Lanza excepción para códigos de error HTTP

            # Verificar que la respuesta sea HTML
            content_type = response.headers.get("content-type", "").lower()
            if "text/html" not in content_type:
                logger.warning(f"La respuesta no es HTML: {content_type}")

            logger.info(
                f"Página obtenida exitosamente: {self.url} (Status: {response.status_code})"
            )
            return response

        except requests.exceptions.Timeout:
            logger.error(
                f"Timeout al conectar con {self.url} después de {self.timeout} segundos"
            )
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Error de conexión con {self.url}: {e}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"Error HTTP al acceder a {self.url}: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error inesperado al acceder a {self.url}: {e}")
        except Exception as e:
            logger.error(f"Error crítico al obtener {self.url}: {e}")

        return None

    def fetch_with_retry(
        self, max_retries: Optional[int] = None
    ) -> Optional[requests.Response]:
        """
        Intenta fetch_page con un número específico de reintentos

        Args:
            max_retries: Número máximo de reintentos (si es None, usa self.max_retries)

        Returns:
            Response o None
        """
        retries = max_retries if max_retries is not None else self.max_retries

        for attempt in range(retries + 1):
            response = self.fetch_page()
            if response:
                return response

            if attempt < retries:
                wait_time = 2**attempt  # 1, 2, 4 segundos
                logger.warning(
                    f"Reintento {attempt + 1}/{retries} en {wait_time} segundos..."
                )
                import time

                time.sleep(wait_time)

        logger.error(f"Fallo después de {retries} reintentos para {self.url}")
        return None

    def set_header(self, key: str, value: str) -> None:
        """
        Actualiza o añade un header por defecto

        Args:
            key: Nombre del header
            value: Valor del header
        """
        self.default_headers[key] = value
        logger.debug(f"Header actualizado: {key} = {value}")

    def set_cookies(self, cookies: Dict) -> None:
        """
        Establece cookies para la sesión

        Args:
            cookies: Diccionario de cookies
        """
        self.session.cookies.update(cookies)
        logger.debug(f"Cookies actualizadas: {list(cookies.keys())}")

    @abstractmethod
    def scrape(self) -> Any:
        """
        Método abstracto que debe ser implementado por cada scraper específico
        Define la lógica de extracción de datos

        Returns:
            Datos extraídos (normalmente List[Dict] o Dict)
        """
        pass

    def close(self) -> None:
        """
        Cierra la sesión de requests
        """
        if self.session:
            self.session.close()
            logger.debug("Sesión cerrada")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - asegura que se cierre la sesión"""
        self.close()
