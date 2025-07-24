FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install OS deps and Python deps from requirements.txt
COPY requirements.txt /app/
RUN apt-get update \
  && apt-get install -y \
       gcc \
       pkg-config \
       default-libmysqlclient-dev \
       libpq-dev \
  && rm -rf /var/lib/apt/lists/* \
  && pip install --upgrade pip \
  && pip install -r requirements.txt

# Copy the rest of the code
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput
ENV SECRET_KEY "U8IbzGYVs17JfBf2YR7mOCEk0HM5IWwgIiToWuu4iPtlW8SqjC"

EXPOSE 8000

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "freeClassifieds.asgi:application"]



