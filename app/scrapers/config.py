# app/scrapers/config.py
GranmmaData = {
    "mundo": ["https://www.granma.cu/mundo", "g-regular-story"],
    "cuba": ["https://www.granma.cu/cuba", "g-regular-story"],
    "deportes": ["https://www.granma.cu/deportes", "g-regular-story"],
    "cultura": ["https://www.granma.cu/cultura", "g-regular-story"],
    "ciencia": ["https://www.granma.cu/ciencia", "g-regular-story"],
}


dataNews = {
    "politica": [
        "http://www.cubadebate.cu/categoria/temas/politica-temas/",
        "politica-temas",
    ],
    "economia": [
        "http://www.cubadebate.cu/categoria/temas/economia-temas/",
        "economia-temas",
    ],
    "cultura": [
        "http://www.cubadebate.cu/categoria/temas/cultura-temas/",
        "cultura-temas",
    ],
    "deporte": [
        "http://www.cubadebate.cu/categoria/temas/deporte-temas/",
        "deporte-temas",
    ],
    "salud": ["http://www.cubadebate.cu/categoria/temas/salud-temas/", "salud-temas"],
    "ciencia": [
        "http://www.cubadebate.cu/categoria/temas/ciencia-y-tecnologia-temas/",
        "tecnologia-temas",
    ],
    "medio_ambiente": [
        "http://www.cubadebate.cu/categoria/temas/medio-ambiente-temas/",
        "medio-ambiente-temas",
    ],
    "medios": [
        "http://www.cubadebate.cu/categoria/temas/medios-temas/",
        "medios-temas",
    ],
    "sociedad": [
        "http://www.cubadebate.cu/categoria/temas/sociedad-temas/",
        "sociedad-temas",
    ],
    "militar y inteligencia": [
        "http://www.cubadebate.cu/categoria/temas/militar-e-inteligencia/",
        "militar-e-inteligencia",
    ],
}

# Selectores basados en el HTML real que me diste
SELECTORES = {
    "articulo": "div.image_post",  # Cada artículo está en un div con clase image_post
    "titulo": "div.title a",  # El título está en div.title > a
    "url": "div.title a",  # La URL está en el mismo a
    "fecha": "time",  # La fecha está en tag time
    "fecha_atributo": "datetime",  # El atributo datetime del time
    "resumen": "div.excerpt p",  # El resumen está en div.excerpt > p
    "imagen": "a.left.media img",  # La imagen está en a.left.media > img
    "categorias": "h3.cat_title a",  # Las categorías están en h3.cat_title > a
    "comentarios": "span.comment_count a",
}
