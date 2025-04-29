FROM python:3.12.7-alpine


LABEL maintainer='
author
'

LABEL version='0.0.0-dev.0-build.0'


WORKDIR /code

COPY . /code

RUN apk add --no-cache musl-dev libc-dev libffi-dev gcc && \

    pip install -r requirements.txt --no-cache-dir && \

    apk del gcc musl-dev libc-dev libffi-dev && \

    addgroup webssh && \

    adduser -Ss /bin/false -g webssh webssh && \

    chown -R webssh:webssh /code && \

    chmod -R 555 /code


EXPOSE 8888/tcp

USER webssh

CMD ["python", "run.py", "--port=$PORT", "--address=0.0.0.0"]
