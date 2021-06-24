FROM python:3.8-slim-buster
RUN apt-get update \
  && apt-get install -y --no-install-recommends procps \
  && apt-get purge -y --auto-remove \
  && rm -rf /var/lib/apt/lists/*

RUN pip3 install py-spy psutil typer pydantic
COPY lookup_pid.py /
RUN chmod a+x /lookup_pid.py

CMD exec /bin/bash -c "trap : TERM INT; sleep infinity & wait"
