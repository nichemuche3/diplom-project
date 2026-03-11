# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем системные зависимости 
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt
COPY backend/requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY backend/ .

# Создаем директорию для статических файлов
RUN mkdir -p /app/static /app/media

# Указываем порт
EXPOSE 8000

# Команда для запуска
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]