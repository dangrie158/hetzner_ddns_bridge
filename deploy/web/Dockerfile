FROM python:3.11-alpine

RUN apk add python3-dev build-base linux-headers pcre-dev libffi-dev git && \
    pip install poetry

RUN mkdir /hetzner_ddns
WORKDIR /hetzner_ddns

COPY poetry.lock pyproject.toml /hetzner_ddns/
RUN poetry install --no-dev --no-interaction

COPY . /hetzner_ddns/
EXPOSE 80

CMD sh -c "poetry run python -m hetzner_ddns"
