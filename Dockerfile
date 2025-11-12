# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# copy only requirements first for caching
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# copy the rest
COPY . /app

EXPOSE 5000

CMD ["python", "app.py"]
