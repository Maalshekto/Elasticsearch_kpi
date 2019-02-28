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


TAG_STATUS = 'status'
TEST_NAME = "gc_state_test"
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

    error_message =  { "message" : "KO", "cause" : message, "name": TEST_NAME }


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
    nodes = es.nodes.stats(metric=['jvm'])["nodes"]

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

