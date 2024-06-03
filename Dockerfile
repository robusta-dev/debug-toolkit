
FROM python:3.12-slim as builder

ENV LANG=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/venv/bin:$PATH"

WORKDIR /app
RUN apt-get update \
  && apt-get install -y --no-install-recommends procps gdb git curl \
  && apt-get install -y gcc\
  && dpkg --add-architecture arm64 \
  && apt-get purge -y --auto-remove \
  && rm -rf /var/lib/apt/lists/*

RUN pip install poetry==1.6.1
RUN poetry config virtualenvs.create false
COPY poetry.lock pyproject.toml /app/

COPY src /app/src

RUN poetry install

RUN apt-get remove -y gcc
RUN apt-get autoremove -y

# -u disables stdout buffering https://stackoverflow.com/questions/107705/disable-output-buffering
# TODO: use -u in developer builds only
CMD exec /bin/bash -c "trap : TERM INT; sleep infinity & wait"

