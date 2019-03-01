#      __     ____ ____   ____   ___     ____   ____ ______ _____
#     / /    /  _// __ ) / __ \ /   |   / __ \ /  _// ____// ___/
#    / /     / / / __  |/ /_/ // /| |  / /_/ / / / / __/   \__ \
#   / /___ _/ / / /_/ // _, _// ___ | / _, _/_/ / / /___  ___/ /
#  /_____//___//_____//_/ |_|/_/  |_|/_/ |_|/___//_____/ /____/
#

from elasticsearch import Elasticsearch, AuthenticationException
import os
import sys
import json
import socket
import random
from datetime import datetime
import logging
from time import time, sleep
import math

#     ______ ____   _   __ _____ ______ ___     _   __ ______ _____
#    / ____// __ \ / | / // ___//_  __//   |   / | / //_  __// ___/
#   / /    / / / //  |/ / \__ \  / /  / /| |  /  |/ /  / /   \__ \
#  / /___ / /_/ // /|  / ___/ / / /  / ___ | / /|  /  / /   ___/ /
#  \____/ \____//_/ |_/ /____/ /_/  /_/  |_|/_/ |_/  /_/   /____/
#

TAG_STATUS = 'status'
GREEN_STATUS = 'green'
TEST_NB_DOC_WRITE = 100
TEST_NAME = "elastic_writing_test"
SYSTEM_RETURN_CODE_ERROR = 0
DELETE_AFTER_SUCCESS_FLAG=True
TIMEOUT_TEST_SOCKET_LEVEL = 3
TAG_ROLE = 'node.role'
FLAG_DATA_ROLE = 'd'

#      __  __ ______ __     ____   ______ ____       ______ __  __ _   __ ______ ______ ____ ____   _   __ _____
#     / / / // ____// /    / __ \ / ____// __ \     / ____// / / // | / // ____//_  __//  _// __ \ / | / // ___/
#    / /_/ // __/  / /    / /_/ // __/  / /_/ /    / /_   / / / //  |/ // /      / /   / / / / / //  |/ / \__ \
#   / __  // /___ / /___ / ____// /___ / _, _/    / __/  / /_/ // /|  // /___   / /  _/ / / /_/ // /|  / ___/ /
#  /_/ /_//_____//_____//_/    /_____//_/ |_|    /_/     \____//_/ |_/ \____/  /_/  /___/ \____//_/ |_/ /____/
#


def print_ko_message_and_exit(message, exception = None):
    """Print error messages in JSON format indicating cause.

    Keyword arguments:
        message -- The custom error message.
        exception -- if the error is due to exception (default None)
    """

    if exception:
        if hasattr(exception, 'message'):
            message += exception.message
        else:
            message += str(exception)

    error_message =  { "message" : "KO", "cause" : message, "name" : TEST_NAME }
    print(json.dumps(error_message))
    sys.exit(SYSTEM_RETURN_CODE_ERROR)

def socket_level_test(host, port):
    """test for knowing if a node has a data role according
           to nodes data.

            Keyword arguments:
                data -- The nodes data with 'node.role' field.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT_TEST_SOCKET_LEVEL)
    res = sock.connect_ex((host, port))
    return res == 0




#      __  ___ ___     ____ _   __     _____  ______ ____   ____ ____  ______
#     /  |/  //   |   /  _// | / /    / ___/ / ____// __ \ /  _// __ \/_  __/
#    / /|_/ // /| |   / / /  |/ /     \__ \ / /    / /_/ / / / / /_/ / / /
#   / /  / // ___ | _/ / / /|  /     ___/ // /___ / _, _/_/ / / ____/ / /
#  /_/  /_//_/  |_|/___//_/ |_/     /____/ \____//_/ |_|/___//_/     /_/
#

# Shut urllib error message as we catch them
# at Elasticsearch level.
urllib3_logger = logging.getLogger('urllib3')
urllib3_logger.setLevel(logging.CRITICAL)

try:
    # Retrieve inputs from ES_PARAMS or multiples environment variables.	
	nb_to_write = int(os.getenv('ES_NB_DOCS') or TEST_NB_DOC_WRITE)
	es_params = os.getenv('ES_PARAMS') or ""
	if es_params is "":
		es_param = dict()
		# Optional inputs
		es_user = os.getenv('ES_USER') or 'elastic'
		es_scheme = os.getenv('ES_SCHEME') or 'https'
		es_capath = os.getenv('ES_PATH') or ""
		

		es_param["port"] = int(os.environ['ES_PORT'])
		es_param["host"] = os.environ['ES_HOST']
		es_param["http_auth"] = [es_user, os.environ['ES_PWD']]
		es_param["scheme"] = es_scheme
		if es_capath != "":
			es_param["ca_certs"] = es_capath

		es_params = json.dumps([es_param])

	json_acceptable_string = es_params.replace("'", "\"")
	es_params = json.loads(json_acceptable_string)

    # hosts reachable control:
	for param in es_params:
		if not socket_level_test(param['host'], param['port']):
			print_ko_message_and_exit(param['host'] + ":" + str(param['port']) + " not reachable - Check port.")

except socket.gaierror:
    print_ko_message_and_exit("Host not reachable - Check host.")
except ValueError as ve:
    print_ko_message_and_exit('Invalid input : ', ve)
except KeyError as ke:
    print_ko_message_and_exit('Variable not set : ', ke)
except Exception as e:
    print_ko_message_and_exit('Generic error : ', e)


try:
    # Retrieve data from Elasticsearch.
	es = Elasticsearch(es_params)
	health = es.cluster.health()
except AuthenticationException as ae:
	print_ko_message_and_exit('Invalid password or login')
except Exception as e:
	print_ko_message_and_exit('Generic error : ', e)

if health[TAG_STATUS] != GREEN_STATUS:
	print_ko_message_and_exit('Cluster health is not green.')
	# if status is green create new index with 1 shard and 1 replica.
try:
	settings = {
		"settings": {
			"number_of_shards": 1,
			"number_of_replicas" : 1
		}
	}
	es.indices.delete(index='test_elastic_writing_test', ignore=404)
	startTime = time()
	es.indices.create(index='test_elastic_writing_test', body = settings)
except Exception as e:
    print_ko_message_and_exit('Generic error : ', e)	

try:
	# Injection of some random document.
	for i in range(0, nb_to_write):
		doc = {
			'timestamp': datetime.now(),
			'name': "test",
			'value': random.random()
		}
		es.index(index='test_elastic_writing_test', doc_type='record', body = doc)
	
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
	res = es.search(index = "test_elastic_writing_test", body= request)	
	time_total = math.floor((time_first_step + time() - startTime) * 100000)/100 
	#tests on answer:
	
	#aggregation of all records ?
	if res['hits']['total'] != nb_to_write:
		es.indices.delete(index='test_elastic_writing_test')
		print_ko_message_and_exit('Aggregation not done with all documents : ' + str(nb_to_write) + ' expected vs ' + str(res['hits']['total']) + ' retrieved.')
	
	if res['aggregations']['total']['value'] > nb_to_write:
		es.indices.delete(index='test_elastic_writing_test')
		print_ko_message_and_exit('Inconsistent value of aggregation')

	if DELETE_AFTER_SUCCESS_FLAG:
		es.indices.delete(index='test_elastic_writing_test')
except Exception as e:
	es.indices.delete(index='test_elastic_writing_test')
	print_ko_message_and_exit('Generic error : ', e)

json_result =  {"message" : "OK",
                "value" : time_total,
                "name": TEST_NAME}

print(json.dumps(json_result))

