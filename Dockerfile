FROM python:3.12-slim

# Отключаем буферизацию вывода Python (логи видны сразу)
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Копируем весь проект
COPY . .

# Создаем директории для статики и медиа
RUN mkdir -p /app/static /app/media

# Создаем непривилегированного пользователя для безопасности
RUN adduser --disabled-password --no-create-home appuser && \
    chown -R appuser:appuser /app

USER appuser

# Запуск через Gunicorn (для продакшена)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
