FROM python:3.13-slim

# groff and less are needed by `aws help`
RUN set -xe \
  && apt-get update -y \
  && apt-get install -y --no-install-recommends groff less \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY . /src
RUN pip install --no-cache-dir /src

ENTRYPOINT ["saws"]
