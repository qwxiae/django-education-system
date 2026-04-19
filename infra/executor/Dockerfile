FROM python:3.11-slim

RUN useradd -m -u 1000 runner

WORKDIR /app

RUN pip install fastapi uvicorn --no-cache-dir

COPY server.py .

USER runner

EXPOSE 8080

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
