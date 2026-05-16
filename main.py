from app.config.connect_db import connect_db
from app.scrapers.start_scraper import start_scraper


def main():
    connect_db()
    start_scraper()


if __name__ == "__main__":
    main()
