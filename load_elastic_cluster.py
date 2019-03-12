from elasticsearch import Elasticsearch, AuthenticationException, helpers
import json
import random
from datetime import datetime
from time import time, sleep
import math
import os
from utils.elasticsearch_utils import print_ko_message, socket_level_test, \
	get_elasticsearch_params, print_ok_message

TAG_STATUS = 'status'
GREEN_STATUS = 'green'
TEST_NB_DOC_WRITE = 100000
TEST_NAME = "load_sample_data"
SYSTEM_RETURN_CODE_ERROR = 0
DELETE_AFTER_SUCCESS_FLAG=True
PRECISION=2


#      __  ___ ___     ____ _   __     _____  ______ ____   ____ ____  ______
#     /  |/  //   |   /  _// | / /    / ___/ / ____// __ \ /  _// __ \/_  __/
#    / /|_/ // /| |   / / /  |/ /     \__ \ / /    / /_/ / / / / /_/ / / /
#   / /  / // ___ | _/ / / /|  /     ___/ // /___ / _, _/_/ / / ____/ / /
#  /_/  /_//_/  |_|/___//_/ |_/     /____/ \____//_/ |_|/___//_/     /_/
#

nb_to_write = int(os.getenv('ES_NB_DOCS') or TEST_NB_DOC_WRITE)
es_params = get_elasticsearch_params(TEST_NAME)

if len(es_params) == 0:
	print_ko_message("None of provided server is responding.", TEST_NAME)

try:
    # Retrieve data from Elasticsearch.
	es = Elasticsearch(es_params)
	health = es.cluster.health()
except AuthenticationException as ae:
	print_ko_message('Invalid password or login', TEST_NAME)
except Exception as e:
	print_ko_message('Generic error : ',TEST_NAME, e)

if health[TAG_STATUS] != GREEN_STATUS:
	print_ko_message('Cluster health is not green.', TEST_NAME)
	# if status is green create new index with 1 shard and 1 replica.
try:
	settings = {
		"settings": {
			"number_of_shards": 5,
			"number_of_replicas" : 2
		}
	}
	es.indices.delete(index='sample_data', ignore=404)
	startTime = time()
	es.indices.create(index='sample_data', body = settings)
except Exception as e:
    print_ko_message('Generic error : ', TEST_NAME, e)	

try:
	# Injection of some random document
	actions = [
		{
			"_index": "sample_data",
			"_type": "records",
			"_id": i,
			"_source": {
				'timestamp': datetime.now(),
				'name': "sample_data",
				'value': random.random()
			}
		}

		for i in range(0, nb_to_write)
	]
	helpers.bulk(es, actions)
except Exception as e:
	es.indices.delete(index='test_elastic_bulk_writing_test')
	print_ko_message('Generic error : ', TEST_NAME, e)

print_ok_message(100.0, TEST_NAME)