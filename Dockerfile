FROM python:3.12-slim as builder

ENV LANG=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/venv/bin:$PATH"

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends procps gdb \
  && apt-get install -y gcc\
  && dpkg --add-architecture arm64 \
  && apt-get purge -y --auto-remove \
  && rm -rf /var/lib/apt/lists/*
RUN pip install poetry==1.6.1

COPY poetry.lock pyproject.toml /app/

COPY src /app/src

RUN python -m venv /app/venv && \
    . /app/venv/bin/activate && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

FROM python:3.12-slim

RUN apt-get update \
  && apt-get install -y --no-install-recommends procps gdb \
  && dpkg --add-architecture arm64 \
  && apt-get purge -y --auto-remove \
  && rm -rf /var/lib/apt/lists/*


ENV PYTHONUNBUFFERED=1
ENV PATH="/venv/bin:$PATH"
ENV PYTHONPATH=$PYTHONPATH:.:/app
COPY --from=builder /app/venv /venv
COPY --from=builder /app /app

RUN echo '#!/bin/bash\npython /app/src/debug_toolkit/main.py $@' > /usr/bin/debug-toolkit && \
    chmod +x /usr/bin/debug-toolkit

# -u disables stdout buffering https://stackoverflow.com/questions/107705/disable-output-buffering
# TODO: use -u in developer builds only
CMD exec /bin/bash -c "trap : TERM INT; sleep infinity & wait"
