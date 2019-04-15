# Using latest Alpine base version
FROM python:3-alpine

RUN apk add --no-cache wget
RUN apk add --no-cache postgresql-libs
RUN apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev

RUN wget -O /usr/local/bin/dumb-init https://github.com/Yelp/dumb-init/releases/download/v1.2.2/dumb-init_1.2.2_amd64
RUN chmod +x /usr/local/bin/dumb-init
RUN pip install psycopg2 
RUN pip install kafka-python
RUN mkdir /app

RUN apk --purge del .build-deps

COPY kafka_postgres_converter.py /app

ENTRYPOINT [ "dumb-init", "--" ]
CMD [ "python", "/app/kafka_postgres_converter.py" ]
