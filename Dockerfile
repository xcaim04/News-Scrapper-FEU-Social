FROM python:3.10-alpine

# Definir el directorio de trabajo
WORKDIR /app

# Copiar e instalar dependencias primero (aprovecha la caché de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código del proyecto
COPY . .

ENTRYPOINT [ "python", "main.py" ]
