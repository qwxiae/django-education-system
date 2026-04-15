# ===============================
# Stage 1: Builder
# ===============================
FROM python:3.12-slim AS builder

WORKDIR /app

# === Install build dependencies ===
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    python3-dev \
    cargo \
    libjpeg-dev \
    zlib1g-dev \
    libtiff5-dev \
    && rm -rf /var/lib/apt/lists/*
    
COPY requirements.txt .
RUN pip install --upgrade pip


# === Copy requirements and install Python packages into /install ===

# Using pip
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# ===============================
# Stage 2: Final image
# ===============================
FROM python:3.12-slim

WORKDIR /app

# === Copy installed Python packages from builder ===
COPY --from=builder /install /usr/local

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && python manage.py seed_lessons && gunicorn config.wsgi:application --bind 0.0.0.0:8000"]