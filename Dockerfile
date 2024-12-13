FROM python:3.10-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY  . /app
EXPOSE 5000

RUN useradd app
USER app

CMD ["python", "app.py"]