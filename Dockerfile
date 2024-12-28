# Этап 1: Сборка зависимостей
FROM python:3.10-slim AS builder
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Этап 2: Сборка приложения
FROM python:3.10-slim
WORKDIR /app
COPY --from=builder /app /app
COPY . /app
EXPOSE 5000
USER root
CMD ["python", "app.py"]

