#      __     ____ ____   ____   ___     ____   ____ ______ _____
#     / /    /  _// __ ) / __ \ /   |   / __ \ /  _// ____// ___/
#    / /     / / / __  |/ /_/ // /| |  / /_/ / / / / __/   \__ \
#   / /___ _/ / / /_/ // _, _// ___ | / _, _/_/ / / /___  ___/ /
#  /_____//___//_____//_/ |_|/_/  |_|/_/ |_|/___//_____/ /____/
#

from elasticsearch import Elasticsearch, AuthenticationException
import json
from packaging import version
from utils.elasticsearch_utils import print_ko_message,socket_level_test, \
    get_elasticsearch_params, print_ok_message

#     ______ ____   _   __ _____ ______ ___     _   __ ______ _____
#    / ____// __ \ / | / // ___//_  __//   |   / | / //_  __// ___/
#   / /    / / / //  |/ / \__ \  / /  / /| |  /  |/ /  / /   \__ \
#  / /___ / /_/ // /|  / ___/ / / /  / ___ | / /|  /  / /   ___/ /
#  \____/ \____//_/ |_/ /____/ /_/  /_/  |_|/_/ |_/  /_/   /____/
#


TAG_STATUS = 'status'
AFTER_6 = '6'

SYSTEM_RETURN_CODE_ERROR = 0

TIMEOUT_TEST_SOCKET_LEVEL = 3
TEST_ERROR_NAME = 'get_bulk_queue_size'
FLAG_DATA_ROLE = 'd'


#      __  ___ ___     ____ _   __     _____  ______ ____   ____ ____  ______
#     /  |/  //   |   /  _// | / /    / ___/ / ____// __ \ /  _// __ \/_  __/
#    / /|_/ // /| |   / / /  |/ /     \__ \ / /    / /_/ / / / / /_/ / / /
#   / /  / // ___ | _/ / / /|  /     ___/ // /___ / _, _/_/ / / ____/ / /
#  /_/  /_//_/  |_|/___//_/ |_/     /____/ \____//_/ |_|/___//_/     /_/
#

es_params = get_elasticsearch_params(TEST_ERROR_NAME)

try:
    # Retrieve data from Elasticsearch.
    es = Elasticsearch(es_params)

    es_version = es.cluster.stats()['nodes']['versions'][0]
    if version.parse(es_version) > version.parse(AFTER_6):
        thread = 'write'
    else:
        thread = 'bulk'
    nodes = es.cat.thread_pool(thread_pool_patterns=[thread], format='json')

    if len(nodes) == 0:
        print_ko_message(f"No {thread} thread found in threads pool", 
            TEST_ERROR_NAME)

    bulk_active = 0
    bulk_queue = 0
    bulk_rejected = 0
	
    for bulk in nodes:
        bulk_active += int(bulk['active'])
        bulk_queue += int(bulk['queue'])
        bulk_rejected += int(bulk['rejected'])

        print_ok_message(int(bulk['active']), 
            f"bulk_active_{bulk['node_name']}")
        print_ok_message(int(bulk['queue']), 
            f"bulk_queue_{bulk['node_name']}")
        print_ok_message(int(bulk['rejected']), 
            f"bulk_rejected_{bulk['node_name']}")

    print_ok_message(bulk_active, "bulk_active_total")
    print_ok_message(bulk_queue, "bulk_queue_total")
    print_ok_message(bulk_rejected, "bulk_rejected_total")
   

except AuthenticationException as ae:
    print_ko_message('Invalid password or login', TEST_ERROR_NAME)
except Exception as e:
    print_ko_message('Generic error : ', TEST_ERROR_NAME, e)

