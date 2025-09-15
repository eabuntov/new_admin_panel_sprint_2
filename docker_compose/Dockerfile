FROM python:3.13-slim

# Workdir
WORKDIR /app

# Install dependencies
COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Django project
COPY .. .

# Collect static files (not critical in dev, useful in prod)
RUN python manage.py collectstatic --noinput || true