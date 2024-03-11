FROM python:3.8-slim-buster
RUN apt-get update \
  && apt-get install -y --no-install-recommends procps gdb git curl \
  && apt-get install -y gcc python3-dev \
  && dpkg --add-architecture arm64 \
  && apt-get purge -y --auto-remove \
  && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -
RUN /root/.local/bin/poetry config virtualenvs.create false
COPY poetry.lock pyproject.toml /app/
WORKDIR /app/
RUN /root/.local/bin/poetry install --no-interaction --no-root

COPY src /app/src
RUN /root/.local/bin/poetry install

CMD exec /bin/bash -c "trap : TERM INT; sleep infinity & wait"