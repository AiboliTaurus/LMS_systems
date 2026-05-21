FROM python:3.12-slim

# Отключаем буферизацию вывода Python (логи видны сразу)
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Запуск сервера
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]