FROM python:3.12-slim

# Отключаем буферизацию вывода Python (логи видны сразу)
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Копируем весь проект
COPY . .

# Запуск через Gunicorn (для продакшена)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]