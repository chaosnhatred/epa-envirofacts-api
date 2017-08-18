import requests, math
from EPA.Utilities import *
from EPA.Envirofacts.Configuration import *
from time import sleep

__base_query = '/WATER_SYSTEM/STATE_CODE/'
__violation_query = '/VIOLATION/GEOGRAPHIC_AREA'
__service_area_query = '/GEOGRAPHIC_AREA/SERVICE_AREA'
__record_count_limit = 250

return_json_results = True
state = get_state()

@public
def get_all():
    count = get_count()
    idx = 1

    if count > __record_count_limit:
        loops = math.floor(count / __record_count_limit)
    
    begin = 0
    end = __record_count_limit
    result = []
    for l in range(loops):        
        query = '%s%s%s%s/rows/%d:%d/json' % (get_api_url(), __base_query, state, __violation_query, begin, end)
        result += call_rest_api(query, 3600) 

        begin += __record_count_limit
        end += __record_count_limit
        sleep(5)

    return result

@public
def get_count():     
    query = '%s%s%s%s/json/count' % (get_api_url(), __base_query, state, __violation_query)
    count = call_rest_api(query)

    if len(count) >= 0:
        return count[0]['totalqueryresults']

    return 0