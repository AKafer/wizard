FROM python:3.11.5-slim-bullseye
LABEL authors="s-storozhuk"

RUN apt-get update && apt-get upgrade -y && \
  apt-get -y install \
    libpq-dev gcc \
    bash \
    expect \
    curl \
    git \
    htop \
    iputils-ping \
    vim \
    openssl \
    libssl-dev \
    build-essential \
    postgresql-client \
    python3-dev \
    libffi-dev \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache uv==0.6.10

COPY pyproject.toml uv.lock /app/
COPY src/ /app/src
RUN rm -rf /app/src/logs && rm -rf /app/src/static
RUN mkdir /app/src/logs && touch /app/src/logs/app.log
RUN mkdir -p /app/src/static

ENV PYTHONPATH "${PYTHONPATH}:/app/src"
ENV PYTHONUNBUFFERED=TRUE

RUN cd /app && uv pip compile pyproject.toml -o /tmp/req.txt && \
    uv pip install --system -r /tmp/req.txt && \
    rm -f /tmp/req.txt

WORKDIR /app/src