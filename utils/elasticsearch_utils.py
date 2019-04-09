import json
import sys
import socket
import os
from kafka import KafkaProducer

FILTER_NOT_RESPONDING = True
TIMEOUT_TEST_SOCKET_LEVEL = 3
SYSTEM_RETURN_CODE_ERROR = 0
FLAG_DATA_ROLE = 'd'
TAG_ROLE = 'node.role'
OUTPUT_SYSTEM_STDOUT = 1
OUTPUT_SYSTEM_KAFKA = 2
OUTPUT_SYSTEM = OUTPUT_SYSTEM_KAFKA

def output_message_stdout(message):
    print(json.dumps(message))

def output_message_kafka(message):
    producer = KafkaProducer(bootstrap_servers="localhost:9092", batch_size=1)
    producer.send("metrics", message.encode())


def output_message(message):
    switcher = {
        OUTPUT_SYSTEM_STDOUT: output_message_stdout,
        OUTPUT_SYSTEM_KAFKA: output_message_kafka
    }

    func = switcher.get(OUTPUT_SYSTEM, lambda: "nothing")
    return func(message)

def print_ko_message(message, test_name, exception = None):
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

    error_message =  { "message" : "KO", "cause" : message, 'name' : test_name }


    output_message(error_message)
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


def get_elasticsearch_params(test_name):
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

        responding_hosts = []
        # hosts reachable control:
        for param in es_params:
            if not FILTER_NOT_RESPONDING or socket_level_test(param['host'], param['port']):
                responding_hosts.append(param)
                
        return responding_hosts
    except socket.gaierror:
        print_ko_message("Host not reachable - Check host.", test_name)
    except ValueError as ve:
        print_ko_message('Invalid input : ', test_name, ve)
    except KeyError as ke:
        print_ko_message('Variable not set : ', test_name,  ke)
    except Exception as e:
        print_ko_message('Generic error : ',test_name, e)

def is_data_node(data):
    """test for knowing if a node has a data role according
       to nodes data.

        Keyword arguments:
            data -- The nodes data with 'node.role' field.
    """
    role = data[TAG_ROLE]
    return FLAG_DATA_ROLE in role


def print_message(message, value, test_name):
    """Print error messages in JSON format indicating cause.

    Keyword arguments:
        message -- The custom error message.
        exception -- if the error is due to exception (default None)
    """
    ok_message =  { "message" : message, "value" : value, 'name' : test_name }
    output_message(ok_message)

def print_ok_message(value, test_name):
    print_message("OK", value, test_name)
