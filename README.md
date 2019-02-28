# Elasticsearch KPI scripts 
The elasticsearch kpi scripts are programmed in **Python 3.7** and conceived for being executed in Docker container.
All scripts are designed to be used on Elasticsearch with version from 5.X.
All scripts have no command line arguments, retrieving all needed informations from environment variables.
There are generic environment variables for connecting to Elasticsearch server and some script-specific environment variables (Such variables will be described in the corresponding script part).

## Generic environment variables.
Each script try to connect to an elasticsearch server (or pool of servers) and for that, there is two ways :
 1. One **JSON String** variable for all settings using (server/pool) : **ES_PARAMS**
 2. Several **String** variables (one server only) 

### ES_PARAMS
The ES_PARAMS is corresponding of the parameter given to Elasticsearch object of the Elasticsearch python API. 
You can find more details [here](https://elasticsearch-py.readthedocs.io/en/master/api.html#elasticsearch)

**Example** : 
*ES_PARAMS= [{
&nbsp;&nbsp;&nbsp;&nbsp;"**host**": "**my-host.com**",
&nbsp;&nbsp;&nbsp;&nbsp;"**port**": **9200**, 
&nbsp;&nbsp;&nbsp;&nbsp;'**http_auth**': ['**elastic**', '**password**'], 
&nbsp;&nbsp;&nbsp;&nbsp;'**scheme**' : '**https**', 
&nbsp;&nbsp;&nbsp;&nbsp;'**ca_certs**' : "**/app/cacert.pem**"
}]*



**Remarks** : 
**ES_PARAMS** is an array ! Even with one single server pool.
It means also you can declare other elasticsearch servers to connect.

### Multiple environment variables
For one server pool only, you can/shall declare the following variables :

 - **ES_HOST** : Host DNS name or IP - *Mandatory*
 - **ES_PORT** : Elasticsearch port. - *Mandatory*
 - **ES_PWD** : Elasticsearch password - *Mandatory*
 - **ES_USER** : Elasticsearch user - *Optional (default: **"elastic"**)*
 - **ES_SCHEME**: Scheme to use - *Optional (default: **"https"**)*
 - **ES_PATH**: Certificat authorities path - *Optioal (default: **""**)*

**Remarks** :
**ES_PARAMS** should not be set if you want to use those variables.

## Generic JSON outputs : 
The output is displayed on stdout. It is a JSON object with two kind of possible structure :
### Success structure.
The format of the structure in case of success of the test is the following :
{
&nbsp;&nbsp;&nbsp;&nbsp;"**message**":  "**MySuccessMessage**"
&nbsp;&nbsp;&nbsp;&nbsp;"**value**": **42**
&nbsp;&nbsp;&nbsp;&nbsp;"**name**": "**MyTestName**"
}
**Remarks**:
 - "**message**" is generally "**OK**" but can be another **String** value.
 - "**value**" is reserved to  **numeric** value only (**int** or **float**).
 - "**name**" is generally componed of a base test name appended of the name of node or cluster.
 - The JSON object will be displayed on one line by test. 
 
**Example**:
```json
{"message": "OK", "value": 3.9393476530797886, "name": "ratio_cur_heap_alloc_instance-0000000000"}  
{"message": "OK", "value": 8.086029394383324, "name": "ratio_max_heap_alloc_instance-0000000000"}  
{"message": "OK", "value": 1.4881722436872644, "name": "ratio_cur_heap_alloc_instance-0000000001"}  
{"message": "OK", "value": 8.134635472478232, "name": "ratio_max_heap_alloc_instance-0000000001"}  
{"message": "OK", "value": 2.717432486604098, "name": "ratio_cur_heap_alloc_total"}  
{"message": "OK", "value": 8.110259608092015, "name": "ratio_max_heap_alloc_total"}
```
  
### Failure structure.
The format of the structure in case of failure of the test is the following :
{
&nbsp;&nbsp;&nbsp;&nbsp;"**message**":  "**MyFailureMessage**"
&nbsp;&nbsp;&nbsp;&nbsp;"**cause**": **42**
&nbsp;&nbsp;&nbsp;&nbsp;"**name**": "**MyTestName**"
}

**Remarks**:
 - "**message**" is generally "**KO**" but can be another **String** value.
 - "**cause**" is giving more details about the nature of the failure. 
 - "**name**" is only componed of a base test name.
 - The JSON object will be displayed on one line.
 
**Example**:
```json
{"message": "KO", "cause": "No data on node : PRtTyb5", "name":"get_ratio_heap"}
```
## Script *get_ratio_heap.py*

The purpose of this script is to retrieve the elasticseach density, that means the ratio between heap sizes (actually used and max) and indexes allocation size. 
There is no formal Elastic group's recommandations, but there is a nice consensual ratio to maintain above, the **1/24 ratio**.
See the discussion [here](https://discuss.elastic.co/t/elastic-ram-disk-ratio-minimum/132435) for more details. 
Two kinds of ratio will be calculated respectively according to the current and max value of the heap. 
Each ratio will also be calculated within 2 levels of granularity : node and cluster level.
The ratio will be calculated only on node with data role.
### Input variables
There is no special input variables for this script.
### Output 
#### Failure message:
In case of failure, "**message**" will be set to "**KO**" and "**name**" will be set to  "**get_ratio_heap**".

**Example**:
```json
{"message": "KO", "cause": "No data on node : PRtTyb5", "name":"get_ratio_heap"}
```
#### Node level
"**message**" will be set to "**OK**"
"**value**" will be the value of the ratio corresponding to the indicated test in "**name**" field.
"**name**" will have 2 base names : "**ratio_cur_heap_alloc**" and "**ratio_max_heap_alloc**", corresponding respectively with current heap and max heap ratio. This base name is appended of the node name.
#### Cluster level
"**message**" will be set to "**OK**"
"**value**" will be the value of the ratio corresponding to the indicated test in "**name**" field.
"**name**" will have 2 possibles names : "**ratio_cur_heap_alloc_total**" and "**ratio_max_heap_alloc_total**"

**Example**:  

```json
{"message": "OK", "value": 3.9393476530797886, "name": "ratio_cur_heap_alloc_instance-0000000000"}  
{"message": "OK", "value": 8.086029394383324, "name": "ratio_max_heap_alloc_instance-0000000000"}  
{"message": "OK", "value": 1.4881722436872644, "name": "ratio_cur_heap_alloc_instance-0000000001"}  
{"message": "OK", "value": 8.134635472478232, "name": "ratio_max_heap_alloc_instance-0000000001"}  
{"message": "OK", "value": 2.717432486604098, "name": "ratio_cur_heap_alloc_total"}  
{"message": "OK", "value": 8.110259608092015, "name": "ratio_max_heap_alloc_total"}
```

## Script *get_cluster_health.py*

The purpose of this script is simply retrieving the global cluster health status.
More detail about cluster health can be found [here](https://www.elastic.co/guide/en/elasticsearch/guide/master/_cluster_health.html).


### Input variables
There is no special input variables for this script.
### Output 
#### Failure message:
In case of failure, "**message**" will be set to "**KO**" and "**name**" will be set to  "**elastic_cluster_health**".

**Example**:
```json
{"message": "KO", "cause": "Host not reachable - Check host.", "name": "elastic_cluster_health"}
```
#### Success message:
"**message**" can have 3 possible values : "**green**", "**yellow**", "**red**".
"**value**" will be arbitrarily set to 0. 
"**name**" will be set to "**elastic_cluster_health**"
**Example**:  

```json
{"message": "green", "value": 0, "name": "elastic_cluster_health"}
```
## Script *get_bulk_queue_size.py*

The purpose of this script is to retrieve 3 elements of the **bulk** (ES 5.X) or **write** (ES 6.X) threads :

 1. Number of currently active requests.
 2. Number of requests in the queue.
 3. Number of Rejected requests (overflowing the queue) 

The number of requests in the queue should remain low (considering the total size of the queue) or ideally empty.
The number of rejected requests shoud still be 0. If not, you can refer to this [documentation](https://www.elastic.co/blog/why-am-i-seeing-bulk-rejections-in-my-elasticsearch-cluster).

Each element will  be retrieved within 2 levels of granularity : nodes and cluster level.


### Input variables
There is no special input variables for this script.
### Output 
#### Failure message:
In case of failure, "**message**" will be set to "**KO**" and "**name**" will be set to  "**get_bulk_queue_size**".

**Example**:
```json
{"message": "KO", "cause": "Host not reachable - Check host.", "name": "get_bulk_queue_size"}
```
#### Node level
"**message**" will be set to "**OK**"
"**value**" will be the number of requests corresponding to the indicated test in "**name**" field.
"**name**" will have 3 base names : "**bulk_active**", "**bulk_queue**"  "**bulk_rejected**", corresponding to the number of respectively active, queued and rejected requests of bulk/write. This base name is appended of the node name.
#### Cluster level
"**message**" will be set to "**OK**"
"**value**" will be  the number of requests corresponding to the indicated test in "**name**" field.
"**name**" will have 3 possibles names : "**bulk_active_total**", "**bulk_queue_total**" and "**bulk_rejected_total**"

**Example**:  

```json
{"message": "OK", "value": 0, "name": "bulk_active_tiebreaker-0000000002"}
{"message": "OK", "value": 0, "name": "bulk_queue_tiebreaker-0000000002"}
{"message": "OK", "value": 0, "name": "bulk_rejected_tiebreaker-0000000002"}
{"message": "OK", "value": 0, "name": "bulk_active_instance-0000000000"}
{"message": "OK", "value": 0, "name": "bulk_queue_instance-0000000000"}
{"message": "OK", "value": 0, "name": "bulk_rejected_instance-0000000000"}
{"message": "OK", "value": 0, "name": "bulk_active_instance-0000000001"}
{"message": "OK", "value": 0, "name": "bulk_queue_instance-0000000001"}
{"message": "OK", "value": 0, "name": "bulk_rejected_instance-0000000001"}
{"message": "OK", "value": 0, "name": "bulk_active_total"}
{"message": "OK", "value": 0, "name": "bulk_queue_total"}
{"message": "OK", "value": 0, "name": "bulk_rejected_total"}
```

## Script *get_gc_state.py*
The purpose of this script is to retrieve 2 specific elements of the garbage collector :

 1. Old collection count
 2. Old collection time 

These 2 counters should increase slowly over time.
If their values increase more quickly than usual, you can refer [here](https://www.elastic.co/guide/en/elasticsearch/guide/current/_monitoring_individual_nodes.html).


Each element will  be retrieved within 2 levels of granularity : nodes and cluster level.


### Input variables
There is no special input variables for this script.
### Output 
#### Failure message:
In case of failure, "**message**" will be set to "**KO**" and "**name**" will be set to  "**gc_state_test**".

**Example**:
```json
{"message": "KO", "cause": "Host not reachable - Check host.", "name": "gc_state_test"}
```
#### Node level
"**message**" will be set to "**OK**"
"**value**" will be the value of element corresponding to the indicated test in "**name**" field.
"**name**" will have 2 base names : "**gc_old_count_**", "**gc_old_time_**" corresponding  respectively to the old collections number and time. This base name is appended of the node name.
#### Cluster level
"**message**" will be set to "**OK**"
"**value**" will be the value of element corresponding to the indicated test in "**name**" field.
"**name**" will have 2 possibles names : "**gc_old_count_total**" and  "**gc_old_time_total**"

**Example**:  

```json
{"message": "OK", "value": 16, "name": "gc_old_count_instance-0000000000"}
{"message": "OK", "value": 2163, "name": "gc_old_time_instance-0000000000"}
{"message": "OK", "value": 3, "name": "gc_old_count_tiebreaker-0000000002"}
{"message": "OK", "value": 767, "name": "gc_old_time_tiebreaker-0000000002"}
{"message": "OK", "value": 3, "name": "gc_old_count_instance-0000000001"}
{"message": "OK", "value": 439, "name": "gc_old_time_instance-0000000001"}
{"message": "OK", "value": 22, "name": "gc_old_count_total"}
{"message": "OK", "value": 3369, "name": "gc_old_time_total"}
```

## Script *elastic_writing_test.py*
The purpose of this script is to perform an functional test of writing and requesting on 
elasticsearch. The test executes the following procedure :

 1. Connection to Elasticsearch
 2. Suppression of the index generated for the  test  to be sure to be in clean context.
 3. Creation of the index used for the test.
 4. Injection of a number (See **Input variables** part)  of documents. 
 5. Wait for 2 seconds for leaving time to indexation to be completed.
 6. Query of the Elasticsearch using a aggregation (here, a sum)
 7. Suppression of the index.

The step 3, 4 and 6 will be time-measured and this time will be returned as value of the test.

**Remarks** : 
 - Documents are sent **one by one**, one document by injection. 
 - Be aware that the measured time for this test is including network latency.  As there are as many request as there are documents, the latencies can take a considerable amount of time.

### Input variables
There is one spectial variable for this test : **ES_NB_DOCS**.
This variable is optional and have a default value of 100.

**Example**
ES_NB_DOCS=250

### Output 
#### Failure message:
In case of failure, "**message**" will be set to "**KO**" and "**name**" will be set to  "**elastic_writing_test**".

**Example**:
```json
{"message": "KO", "cause": "Host not reachable - Check host.", "name": "elastic_writing_test"}
```
#### Success message:
"**message**" will be set to "**OK**"
"**value**" will be the time measured during the test.
"**name**" will be set to "**elastic_writing_test**".

**Example**:  

```json
{"message": "OK", "value": 33142.22, "name": "elastic_writing_test"}
```

## Script *elastic_bulk_writing_test.py*
The purpose of this script is to perform an functional test of writing and requesting on 
elasticsearch. The test executes the following procedure :

 1. Connection to Elasticsearch
 2. Suppression of the index generated for the  test  to be sure to be in clean context.
 3. Creation of the index used for the test.
 4. Injection of a number (See **Input variables** part)  of documents. 
 5. Wait for 2 seconds for leaving time to indexation to be completed.
 6. Query of the Elasticsearch using a aggregation (here, a sum)
 7. Suppression of the index.

The step 3, 4 and 6 will be time-measured and this time will be returned as value of the test.

**Remarks** : 
 - Documents are sent in **one single bulk**, all documents in one injection. 
 - Be aware that the measured time for this test is including network latency.  The latency will have less impact than for **one by one** test but can still have some impacts.

### Input variables
There is one spectial variable for this test : **ES_NB_DOCS**.
This variable is optional and have a default value of 10000.

**Example**
ES_NB_DOCS=250

### Output 
#### Failure message:
In case of failure, "**message**" will be set to "**KO**" and "**name**" will be set to  "**elastic_writing_test**".

**Example**:
```json
{"message": "KO", "cause": "Host not reachable - Check host.", "name": "elastic_bulk_writing_test"}
```
#### Success message:
"**message**" will be set to "**OK**"
"**value**" will be the time measured during the test.
"**name**" will be set to "**elastic_writing_test**".

**Example**:  

```json
{"message": "OK", "value": 21268.82, "name": "elastic_bulk_writing_test"}
```
