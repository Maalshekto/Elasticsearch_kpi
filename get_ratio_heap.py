#      __     ____ ____   ____   ___     ____   ____ ______ _____
#     / /    /  _// __ ) / __ \ /   |   / __ \ /  _// ____// ___/
#    / /     / / / __  |/ /_/ // /| |  / /_/ / / / / __/   \__ \
#   / /___ _/ / / /_/ // _, _// ___ | / _, _/_/ / / /___  ___/ /
#  /_____//___//_____//_/ |_|/_/  |_|/_/ |_|/___//_____/ /____/
#

from elasticsearch import Elasticsearch, AuthenticationException
import humanfriendly
import json
from utils.elasticsearch_utils import print_ko_message, socket_level_test, \
    get_elasticsearch_params, is_data_node, print_ok_message

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
TAG_NAME = 'name'
TAG_RATIO_CUR_HEAP_DISK_INDICES = 'ratio.cur_heap_disk_indices'
TAG_RATIO_MAX_HEAP_DISK_INDICES = 'ratio.max_heap_disk_indices'
TAG_NAME_ALLOC = 'node'
TAG_ROLE = 'node.role'
TEST_ERROR_NAME = 'get_ratio_heap'



#      __  __ ______ __     ____   ______ ____   _____ 
#     / / / // ____// /    / __ \ / ____// __ \ / ___/
#    / /_/ // __/  / /    / /_/ // __/  / /_/ / \__ \   
#   / __  // /___ / /___ / ____// /___ / _, _/ ___/ /  
#  /_/ /_//_____//_____//_/    /_____//_/ |_| /____/  
#

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
    


#      __  ___ ___     ____ _   __     _____  ______ ____   ____ ____  ______
#     /  |/  //   |   /  _// | / /    / ___/ / ____// __ \ /  _// __ \/_  __/
#    / /|_/ // /| |   / / /  |/ /     \__ \ / /    / /_/ / / / / /_/ / / /
#   / /  / // ___ | _/ / / /|  /     ___/ // /___ / _, _/_/ / / ____/ / /
#  /_/  /_//_/  |_|/___//_/ |_/     /____/ \____//_/ |_|/___//_/     /_/
#

es_params = get_elasticsearch_params(TEST_ERROR_NAME)

if len(es_params) == 0:
    print_ko_message("None of provided server is responding.", TEST_ERROR_NAME)

try:
    # Retrieve data from Elasticsearch.
    es = Elasticsearch(es_params)
    memory_infos = es.cat.nodes(
        h=[TAG_HEAP_USAGE, TAG_HEAP_MAX, TAG_RAM_MAX, TAG_ROLE, TAG_NAME], 
        format='json')
    alloc = es.cat.allocation(h=[TAG_DISK_USAGE, TAG_NAME_ALLOC], format='json',
        bytes="b")

except AuthenticationException as ae:
    print_ko_message('Invalid password or login', TEST_ERROR_NAME)
except Exception as e:
    print_ko_message('Generic error : ', TEST_ERROR_NAME, e)


# Ratio calculation and JSON output creation.
node_infos = {}

for node in alloc:
    node_infos[node[TAG_NAME_ALLOC]] = {}
    node_infos[node[TAG_NAME_ALLOC]][TAG_DISK_USAGE] = \
        get_value_from_tag(node, TAG_DISK_USAGE)

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
            print_ko_message(f"No data on node : {node[TAG_NAME]}", 
                TEST_ERROR_NAME)

        print_ok_message(float(heap_usage)/float(disk_usage), 
            f"ratio_cur_heap_alloc_{node[TAG_NAME]}")
        print_ok_message(float(heap_max)/float(disk_usage), 
            f"ratio_max_heap_alloc_{node[TAG_NAME]}")
        
ratio_current_heap_disk = float(heap_usage_total)/float(disk_usage_total)
ratio_max_heap_disk = float(heap_max_total)/float(disk_usage_total)

print_ok_message(ratio_current_heap_disk, "ratio_cur_heap_alloc_total")
print_ok_message(ratio_max_heap_disk, "ratio_max_heap_alloc_total")

