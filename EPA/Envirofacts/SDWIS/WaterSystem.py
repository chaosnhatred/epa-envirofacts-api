# -*- coding: utf-8 -*-

from math import floor
from time import sleep
from .. import Configuration
from ...__Utilities.__utilities import *

__base_query = '/WATER_SYSTEM/'
__state_query = 'STATE_CODE/'
__water_system_query = 'PWSID/=/'
__record_count_limit = 250
__batch_delay = 2
__api = RestAPI(Configuration.api_url, Configuration.api_result_format)

#return_raw_results = False
#state = Configuration.state

def __get_count(query):
    if not query or len(query) <= 0:
        raise ValueError('query cannot be empty or null.')

    #The Envirofacts api does not return the count properly in any other format but JSON or XML.
    __api.api_result_type = RestApiResultType.JSON      
    query = '%s/json/count' % (query)
    count = __api.get(query)    
    __api.api_result_type = Configuration.api_result_format
        
    return count[0]['totalqueryresults']

@public
def get_count():
    return __get_count(__base_query)

@public
def get_count_by_state(state = Configuration.state):       
    query = '%s%s%s' % (__base_query, __state_query, state)
    return __get_count(query)

def __get(query, count):
    if not query:
        raise ValueError('query cannot be empty or null.')
    
    if not count or type(count) is not int:
        raise ValueError('count is not an integer or is null.')

    __api.api_result_type = Configuration.api_result_format
    count = count - 1 
    idx = 1
    loops = 1
    begin = 0
    end = count  

    if count > __record_count_limit:
        end = __record_count_limit - 1
        loops = floor(count / __record_count_limit)
            
    result = []
    for l in range(loops):                
        query = '%s/rows/%d:%d/%s' % (query, begin, end, Configuration.api_result_format)       
        result += __api.get(query, 3600)

        begin += __record_count_limit
        end += __record_count_limit
        sleep(__batch_delay)

    return result

@public
def get(count = None):
    if not count or count <= 0:
        count = get_count()

    return __get(__base_query, count)

@public
def get_by_state(state = Configuration.state, count = None):
    if not count or count <= 0:
        count = get_count_by_state(state)

    query = '%s%s%s' % (__base_query, __state_query, state)
    return __get(query, count)