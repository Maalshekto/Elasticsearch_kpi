#      __     ____ ____   ____   ___     ____   ____ ______ _____
#     / /    /  _// __ ) / __ \ /   |   / __ \ /  _// ____// ___/
#    / /     / / / __  |/ /_/ // /| |  / /_/ / / / / __/   \__ \
#   / /___ _/ / / /_/ // _, _// ___ | / _, _/_/ / / /___  ___/ /
#  /_____//___//_____//_/ |_|/_/  |_|/_/ |_|/___//_____/ /____/
#

from elasticsearch import Elasticsearch, AuthenticationException
import humanfriendly
import os
import sys
import json
import socket

#     ______ ____   _   __ _____ ______ ___     _   __ ______ _____
#    / ____// __ \ / | / // ___//_  __//   |   / | / //_  __// ___/
#   / /    / / / //  |/ / \__ \  / /  / /| |  /  |/ /  / /   \__ \
#  / /___ / /_/ // /|  / ___/ / / /  / ___ | / /|  /  / /   ___/ /
#  \____/ \____//_/ |_/ /____/ /_/  /_/  |_|/_/ |_/  /_/   /____/
#

TAG_HEAP_USAGE = 'heap.current'
TAG_HEAP_MAX = 'heap.max'
TAG_RAM_MAX = 'ram.max'
TAG_DISK_USAGE = 'disk.indices'
TAG_ROLE = 'node.role'
TAG_NAME = 'name'
TAG_RATIO_CUR_HEAP_DISK_INDICES = 'ratio.cur_heap_disk_indices'
TAG_RATIO_MAX_HEAP_DISK_INDICES = 'ratio.max_heap_disk_indices'
TAG_NAME_ALLOC = 'node'

SYSTEM_RETURN_CODE_ERROR = 0

TIMEOUT_TEST_SOCKET_LEVEL = 3

FLAG_DATA_ROLE = 'd'

#      __  __ ______ __     ____   ______ ____       ______ __  __ _   __ ______ ______ ____ ____   _   __ _____
#     / / / // ____// /    / __ \ / ____// __ \     / ____// / / // | / // ____//_  __//  _// __ \ / | / // ___/
#    / /_/ // __/  / /    / /_/ // __/  / /_/ /    / /_   / / / //  |/ // /      / /   / / / / / //  |/ / \__ \
#   / __  // /___ / /___ / ____// /___ / _, _/    / __/  / /_/ // /|  // /___   / /  _/ / / /_/ // /|  / ___/ /
#  /_/ /_//_____//_____//_/    /_____//_/ |_|    /_/     \____//_/ |_/ \____/  /_/  /___/ \____//_/ |_/ /____/
#


def print_ko_message(message, exception = None):
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

    error_message =  { "message" : "KO", "cause" : message, name :  }


    print(json.dumps(error_message))
    sys.exit(SYSTEM_RETURN_CODE_ERROR)


def get_value_from_hr_tag(hr_value, tag):
    """Retrieve and convert an human readable size of a specified
       tag to a full numeric value.

    Keyword arguments:
        hr_value -- The data containing human readable value
        tag -- the tag used to retrieved the human readable value
    """

    res = humanfriendly.parse_size(hr_value[tag], binary = True)
    return res if res else 0
	
def get_value_from_tag(data, tag):
    """Retrieve a element of a specified tag from data.

    Keyword arguments:
        data -- The data containing expected value
        tag -- the tag used to retrieved the value
    """
    res = data[tag]
    return int(res) if res else 0
	
def is_data_node(data):
    """test for knowing if a node has a data role according
       to nodes data.

        Keyword arguments:
            data -- The nodes data with 'node.role' field.
    """
    role = data[TAG_ROLE]
    return FLAG_DATA_ROLE in role

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


try:
    # Retrieve inputs from ES_PARAMS or multiples environment variables.
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
            print_ko_message(param['host'] + ":" + str(param['port']) + " not reachable - Check port.")

except socket.gaierror:
    print_ko_message("Host not reachable - Check host.")
except ValueError as ve:
    print_ko_message('Invalid input : ', ve)
except KeyError as ke:
    print_ko_message('Variable not set : ', ke)
except Exception as e:
    print_ko_message('Generic error : ', e)


try:
    # Retrieve data from Elasticsearch.
    es = Elasticsearch(es_params)
    memory_infos = es.cat.nodes(h=[TAG_HEAP_USAGE, TAG_HEAP_MAX, TAG_RAM_MAX, TAG_ROLE, TAG_NAME], format='json')
    alloc = es.cat.allocation(h=[TAG_DISK_USAGE, TAG_NAME_ALLOC], format='json', bytes="b")

except AuthenticationException as ae:
    print_ko_message('Invalid password or login')
except Exception as e:
    print_ko_message('Generic error : ', e)


# Ratio calculation and JSON output creation.
node_infos = {}

for node in alloc:
    node_infos[node[TAG_NAME_ALLOC]] = {}
    node_infos[node[TAG_NAME_ALLOC]][TAG_DISK_USAGE] = get_value_from_tag(node, TAG_DISK_USAGE)

disk_usage_total = 0 
heap_usage_total = 0
heap_max_total = 0


for node in memory_infos:
    if is_data_node(node):
        heap_usage = get_value_from_hr_tag(node, TAG_HEAP_USAGE)
        heap_usage_total += heap_usage
        disk_usage = node_infos[node[TAG_NAME]][TAG_DISK_USAGE]
        disk_usage_total += disk_usage
        heap_max = get_value_from_hr_tag(node, TAG_HEAP_MAX)
        heap_max_total += heap_max
        if disk_usage == 0:
            print_ko_message('No data on node : ' + node[TAG_NAME])

        json_result =  {"message" : "OK",
                        "value" : float(heap_usage)/float(disk_usage),
                        "name": "ratio_cur_heap_alloc_" + node[TAG_NAME]}

        print(json.dumps(json_result))

        json_result = {"message": "OK",
                       "value": float(heap_max) / float(disk_usage),
                       "name": "ratio_max_heap_alloc_" + node[TAG_NAME]}

        print(json.dumps(json_result))
        
ratio_current_heap_disk = float(heap_usage_total)/float(disk_usage_total)
ratio_max_heap_disk = float(heap_max_total)/float(disk_usage_total)

json_result =  {"message" : "OK",
                        "value" : ratio_current_heap_disk,
                        "name": "ratio_cur_heap_alloc_total"}

print(json.dumps(json_result))

json_result = {"message": "OK",
               "value": ratio_max_heap_disk,
               "name": "ratio_max_heap_alloc_total"}

print(json.dumps(json_result))