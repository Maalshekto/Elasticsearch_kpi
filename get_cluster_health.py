#      __     ____ ____   ____   ___     ____   ____ ______ _____
#     / /    /  _// __ ) / __ \ /   |   / __ \ /  _// ____// ___/
#    / /     / / / __  |/ /_/ // /| |  / /_/ / / / / __/   \__ \
#   / /___ _/ / / /_/ // _, _// ___ | / _, _/_/ / / /___  ___/ /
#  /_____//___//_____//_/ |_|/_/  |_|/_/ |_|/___//_____/ /____/
#

from elasticsearch import Elasticsearch, AuthenticationException
import json
from utils.elasticsearch_utils import print_ko_message, socket_level_test, get_elasticsearch_params
#     ______ ____   _   __ _____ ______ ___     _   __ ______ _____
#    / ____// __ \ / | / // ___//_  __//   |   / | / //_  __// ___/
#   / /    / / / //  |/ / \__ \  / /  / /| |  /  |/ /  / /   \__ \
#  / /___ / /_/ // /|  / ___/ / / /  / ___ | / /|  /  / /   ___/ /
#  \____/ \____//_/ |_/ /____/ /_/  /_/  |_|/_/ |_/  /_/   /____/
#


TAG_STATUS = 'status'
TEST_ERROR_NAME = 'elastic_cluster_health'


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
    health = es.cluster.health()
except AuthenticationException as ae:
    print_ko_message('Invalid password or login', TEST_ERROR_NAME)
except Exception as e:
    print_ko_message('Generic error : ',TEST_ERROR_NAME, e)


json_result =  {"message" : health[TAG_STATUS],
                "value" : 0,
                "name": TEST_ERROR_NAME}

print(json.dumps(json_result))

