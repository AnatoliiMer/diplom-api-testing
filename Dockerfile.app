FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копирование зависимостей
COPY app/requirements.app.txt .
RUN pip install --no-cache-dir -r requirements.app.txt

# Копирование кода приложения
COPY app/ .

# Настройка переменных окружения
ENV FLASK_ENV=development
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Создание непривилегированного пользователя
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Healthcheck с правильным таймаутом
HEALTHCHECK --interval=5s --timeout=3s --start-period=15s --retries=5 \
    CMD curl -f http://localhost:5000/health || exit 1

EXPOSE 5000

CMD ["python", "app.py"]