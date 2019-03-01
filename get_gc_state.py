#      __     ____ ____   ____   ___     ____   ____ ______ _____
#     / /    /  _// __ ) / __ \ /   |   / __ \ /  _// ____// ___/
#    / /     / / / __  |/ /_/ // /| |  / /_/ / / / / __/   \__ \
#   / /___ _/ / / /_/ // _, _// ___ | / _, _/_/ / / /___  ___/ /
#  /_____//___//_____//_/ |_|/_/  |_|/_/ |_|/___//_____/ /____/
#

from elasticsearch import Elasticsearch, AuthenticationException
import json
from utils.elasticsearch_utils import print_ko_message,socket_level_test, get_elasticsearch_params
#     ______ ____   _   __ _____ ______ ___     _   __ ______ _____
#    / ____// __ \ / | / // ___//_  __//   |   / | / //_  __// ___/
#   / /    / / / //  |/ / \__ \  / /  / /| |  /  |/ /  / /   \__ \
#  / /___ / /_/ // /|  / ___/ / / /  / ___ | / /|  /  / /   ___/ /
#  \____/ \____//_/ |_/ /____/ /_/  /_/  |_|/_/ |_/  /_/   /____/
#

TAG_GC = 'gc'
TEST_NAME = "gc_state_test"
SYSTEM_RETURN_CODE_ERROR = 0
TIMEOUT_TEST_SOCKET_LEVEL = 3

FLAG_DATA_ROLE = 'd'


#      __  ___ ___     ____ _   __     _____  ______ ____   ____ ____  ______
#     /  |/  //   |   /  _// | / /    / ___/ / ____// __ \ /  _// __ \/_  __/
#    / /|_/ // /| |   / / /  |/ /     \__ \ / /    / /_/ / / / / /_/ / / /
#   / /  / // ___ | _/ / / /|  /     ___/ // /___ / _, _/_/ / / ____/ / /
#  /_/  /_//_/  |_|/___//_/ |_/     /____/ \____//_/ |_|/___//_/     /_/
#

es_params = get_elasticsearch_params(TEST_NAME)

try:
    # Retrieve data from Elasticsearch.
    es = Elasticsearch(es_params)
    nodes = es.nodes.stats(metric=['jvm'])['nodes']

    if len(nodes) == 0:
        print_ko_message('no nodes found')

    gc_old_count = 0
    gc_old_time = 0

	
    for node in nodes:
        gc_old = nodes[node]['jvm']['gc']['collectors']['old']
        gc_old_count += int(gc_old['collection_count'])
        gc_old_time += int(gc_old['collection_time_in_millis'])


        json_result = { "message": "OK",
                        "value": int(gc_old['collection_count']),
                        "name": "gc_old_count_" + nodes[node]['name'] }

        print(json.dumps(json_result))

        json_result = { "message": "OK",
                        "value": int(gc_old['collection_time_in_millis']),
                        "name": "gc_old_time_" + nodes[node]['name']}

        print(json.dumps(json_result))


    json_result = {"message": "OK",
                   "value": gc_old_count,
                   "name": "gc_old_count_total"}

    print(json.dumps(json_result))

    json_result = {"message": "OK",
                   "value": gc_old_time,
                   "name": "gc_old_time_total"}

    print(json.dumps(json_result))



except AuthenticationException as ae:
    print_ko_message('Invalid password or login')
except Exception as e:
    print_ko_message('Generic error : ', e)

