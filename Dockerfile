FROM python:3.9-slim

# Устанавливаем netcat для ожидания PostgreSQL
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh

ENV FLASK_APP=app
ENV FLASK_ENV=development

EXPOSE 5000

CMD ["./entrypoint.sh"]