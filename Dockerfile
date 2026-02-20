# Multi-stage build для оптимизации размера образа
FROM python:3.11-slim AS builder

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Создание виртуального окружения
RUN python -m venv /opt/venv

# Активация venv
ENV PATH="/opt/venv/bin:$PATH"

# Копирование requirements
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# Финальный образ
FROM python:3.11-slim

# Метаданные
LABEL maintainer="your-email@example.com"
LABEL description="Google Sheets JSON API"

# Создание пользователя без root прав (безопасность)
RUN useradd -m -u 1000 appuser

# Рабочая директория
WORKDIR /app

# Копирование виртуального окружения из builder
COPY --from=builder /opt/venv /opt/venv

# Установка curl для health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Активация venv
ENV PATH="/opt/venv/bin:$PATH"

# Копирование кода приложения
COPY --chown=appuser:appuser app.py .
COPY --chown=appuser:appuser sheets_client.py .
COPY --chown=appuser:appuser config.py .

# Переключение на непривилегированного пользователя
USER appuser

# Переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8000

# Открытие порта
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Запуск приложения через uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
