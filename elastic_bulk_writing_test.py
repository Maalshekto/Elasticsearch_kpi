#      __     ____ ____   ____   ___  p   ____   ____ ______ _____
#     / /    /  _// __ ) / __ \ /   |   / __ \ /  _// ____// ___/
#    / /     / / / __  |/ /_/ // /| |  / /_/ / / / / __/   \__ \
#   / /___ _/ / / /_/ // _, _// ___ | / _, _/_/ / / /___  ___/ /
#  /_____//___//_____//_/ |_|/_/  |_|/_/ |_|/___//_____/ /____/
#

from elasticsearch import Elasticsearch, AuthenticationException, helpers
import json
import random
from datetime import datetime
from time import time, sleep
import math
import os
from utils.elasticsearch_utils import print_ko_message, socket_level_test, \
	get_elasticsearch_params, print_ok_message

#     ______ ____   _   __ _____ ______ ___     _   __ ______ _____
#    / ____// __ \ / | / // ___//_  __//   |   / | / //_  __// ___/
#   / /    / / / //  |/ / \__ \  / /  / /| |  /  |/ /  / /   \__ \
#  / /___ / /_/ // /|  / ___/ / / /  / ___ | / /|  /  / /   ___/ /
#  \____/ \____//_/ |_/ /____/ /_/  /_/  |_|/_/ |_/  /_/   /____/
#

TAG_STATUS = 'status'
GREEN_STATUS = 'green'
TEST_NB_DOC_WRITE = 10000
TEST_NAME = "elastic_bulk_writing_test"
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
			"number_of_shards": 1,
			"number_of_replicas" : 1
		}
	}
	es.indices.delete(index='test_elastic_bulk_writing_test', ignore=404)
	startTime = time()
	es.indices.create(index='test_elastic_bulk_writing_test', body = settings)
except Exception as e:
    print_ko_message('Generic error : ', TEST_NAME, e)	

try:
	# Injection of some random document
	actions = [
		{
			"_index": "test_elastic_bulk_writing_test",
			"_type": "records",
			"_id": i,
			"_source": {
				'timestamp': datetime.now(),
				'name': "test",
				'value': random.random()
			}
		}

		for i in range(0, nb_to_write)
	]
	helpers.bulk(es, actions)

	# Waiting 2 seconds for indexation to be fully completed.
	time_first_step = time() - startTime
	sleep(2)
	startTime = time()
	# Request with aggregation.
	request = {
		"size": 0, 
		"aggs": {
			"total": {
				"sum": {
					"field": "value"
				}
			}
		}
	}
	res = es.search(index = "test_elastic_bulk_writing_test", body= request)
	time_total_millis = (time_first_step + time() - startTime) * 1000 
	#tests on answer:
	
	nb_retrieved_records = res['hits']['total'] 

	# In version 7.0.0. of elasticsearch, nb_retrieved_records is a dict
	# To retrieve the expected value, we have to use "value" key
	if isinstance(nb_retrieved_records, (dict)):
		nb_retrieved_records = nb_retrieved_records["value"]
		
	#aggregation of all records ?
	if nb_retrieved_records != nb_to_write:	
		es.indices.delete(index='test_elastic_writing_test')
		print_ko_message(f"Aggregation not done with all documents : "
			f"{nb_to_write} expected vs {nb_retrieved_records} retrieved.", 
			TEST_NAME)
		
	if res['aggregations']['total']['value'] > nb_to_write:
		es.indices.delete(index='test_elastic_bulk_writing_test')
		print_ko_message('Inconsistent value of aggregation', TEST_NAME)

	if DELETE_AFTER_SUCCESS_FLAG:
		es.indices.delete(index='test_elastic_bulk_writing_test')
except Exception as e:
	es.indices.delete(index='test_elastic_bulk_writing_test')
	print_ko_message('Generic error : ', TEST_NAME, e)

print_ok_message(float(f"{time_total_millis:.{PRECISION}f}"), TEST_NAME)
