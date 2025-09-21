FROM python:3.10

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UWSGI_PROCESSES=1 \
    UWSGI_THREADS=16 \
    UWSGI_HARAKIRI=240 \
    DJANGO_SETTINGS_MODULE=example.settings

COPY run_uwsgi.sh run_uwsgi.sh
COPY requirements.txt requirements.txt
COPY uwsgi/uwsgi.ini uwsgi.ini

RUN mkdir -p /var/www/static/ \
    && mkdir -p /var/www/media/ \
    && mkdir -p /opt/app/static/ \
    && mkdir -p /opt/app/media/ \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && apt install media-types

COPY . .

EXPOSE 8000

# Collect static files and run migrations before starting uWSGI
CMD python manage.py makemigrations --noinput && \
    python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    uwsgi --strict --ini uwsgi.ini
