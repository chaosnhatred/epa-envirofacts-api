# -*- coding: utf-8 -*-

import re, requests, os, sys, json, threading, csv
from time import sleep
from collections import namedtuple
from contextlib import contextmanager
from io import StringIO
from enum import Enum

def public(f):
    """"Use a decorator to avoid retyping function/class names.

    * Based on an idea by Duncan Booth:
    http://groups.google.com/group/comp.lang.python/msg/11cbb03e09611b8a
    * Improved via a suggestion by Dave Angel:
    http://groups.google.com/group/comp.lang.python/msg/3d400fb22d8a42e1
    """
    all = sys.modules[f.__module__].__dict__.setdefault('__all__', [])
    if f.__name__ not in all:  # Prevent duplicates if run from an IDE.
        all.append(f.__name__)
    return f

@contextmanager
@public
def csv_string_reader(string, to_dict = False):
     with StringIO(string) as in_s:
        try:
            if not csv.Sniffer().sniff(in_s.read(4096)):
                raise ValueError('string is not a valid csv format')
            
            in_s.seek(0)
            if to_dict:
                yield csv.DictReader(in_s)
            else:
                yield csv.reader(in_s)              
        finally:
            in_s.seek(0)

@public
def convert_to_lower_keys(d):
    if isinstance(d, list):
        return [convert_to_lower_keys(v) for v in d]
    elif isinstance(d, dict):
        try:
            return dict((k.lower(), convert_to_lower_keys(v)) for k, v in d.items())
        except:
            return dict((k, convert_to_lower_keys(v)) for k, v in d.items())
    elif isinstance(d, str):
        return d.lower()
    else:
        return d

@public
class RestApiResultType(Enum):
        JSON = 'json'
        XML = 'xml'
        CSV = 'csv'

@public
class RestAPI(object):    
    def __init__(self, api_url, api_result_type=RestApiResultType.JSON):        
        self.__api_url = api_url
        self.api_result_type = api_result_type
        self.return_raw_results = False    
        self.timeout_limit = 300
        self.retries = 5

        if not self.__api_url.endswith('/'):
            self.__api_url += '/'

    def get(self, request, timeout=-1):
        if not request:
            raise ValueError('request cannot be empty or null')
        
        if timeout == -1:
            timeout = self.timeout_limit
        
        get_request = '%s%s' % (self.__api_url, self.__format_request_url(request))
        p4 = re.compile('40[0-9]')
        p5 = re.compile('50[0-9]')

        for attempt in range(self.retries):
            try:
                r = requests.get(get_request, timeout=timeout)
                r.raise_for_status()
                return self.__get_api_result(r)
            except requests.exceptions.Timeout:            
                if attempt == self.retries:
                    raise
                sleep(60)
                timeout += 300            
            except requests.exceptions.HTTPError as e:
                if p4.match(str(e.response.status_code)):
                    if attempt == self.retries:
                        raise
                    sleep(10)
                elif p5.match(str(e.response.status_code)):
                    if attempt == self.retries:
                        raise
                    sleep(120)
                    timeout += 300 

    def __get_api_result(self, result):
        if result and result.status_code == 200: 
            if self.return_raw_results:
                return result.text

            if self.api_result_type == RestApiResultType.JSON:  
                try:   
                    return result.json(object_hook=self.__json_object_hook)
                except json.JSONDecodeError as e:
                    raise ValueError('could not decode api result: %s' % e)
            elif self.api_result_type == RestApiResultType.CSV:
                csv_list = []
                with csv_string_reader(result.text, True) as r:
                    for row in r:
                        row = convert_to_lower_keys(row)                          
                        csv_list.append(row)
                return csv_list
            else:
                return result.text

        return None

    def __json_object_hook(self, d):
        d = convert_to_lower_keys(d)
        return d

    def __format_request_url(self, request):
        if self.__api_url in request:
            request = re.sub(self.__api_url, '', request)

        if request.startswith('/'):
            request = request[1:]

        return request

public(public)


