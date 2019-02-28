FROM python:3-alpine

RUN apk add wget
RUN wget -O /usr/local/bin/dumb-init https://github.com/Yelp/dumb-init/releases/download/v1.2.2/dumb-init_1.2.2_amd64
RUN chmod +x /usr/local/bin/dumb-init
RUN pip install Elasticsearch 
RUN pip install humanfriendly
RUN pip install packaging
RUN mkdir /app

COPY get_ratio_heap.py /app
COPY get_cluster_health.py /app
COPY get_gc_state.py /app
COPY get_bulk_queue_size.py /app
COPY elastic_writing_test.py /app
COPY elastic_bulk_writing_test.py /app

ENTRYPOINT [ "dumb-init", "--" ]
CMD [ "python", "/app/get_ratio_heap.py" ]



