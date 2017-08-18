# -*- coding: utf-8 -*-

import re, requests, os, sys, json
from time import sleep
from collections import namedtuple
from contextlib import contextmanager

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
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout= sys.stdout
        sys.stdout= devnull
        try:  
            yield
        finally:
            sys.stdout= old_stdout

@public
def convert_to_lower_keys(d):
    if isinstance(d, list):
        return [convert_to_lower_keys(v) for v in d]
    elif isinstance(d, dict):
        return dict((k.lower(), convert_to_lower_keys(v)) for k, v in d.items())
    else:
        return d

@public
def call_rest_api(request, timeout_limit=300):
    retries = 5
    p4 = re.compile('40[0-9]')
    p5 = re.compile('50[0-9]')

    for attempt in range(retries):
        try:
            r = requests.get(request, timeout=timeout_limit)
            r.raise_for_status()
            return __get_api_result(r)
        except requests.exceptions.Timeout:            
            if attempt == retries:
                sys.stdout.write('\b a timeout occurred making the api request: %s' % request)
            timer(60)
            timeout_limit += 300            
        except requests.exceptions.HTTPError as e:
            if p4.match(str(e.response.status_code)):
                if attempt == retries:
                    sys.stdout.write('\b url for was not found for request: %s' % request)
                timer()
            elif p5.match(str(e.response.status_code)):
                if attempt == retries:
                    sys.stdout.write('\b a server error occurred making the api request: %s' % request)
                timer(120)
                timeout_limit += 300
            else:
                print(e)
                break
        except Exception as e:
            print(e)
            break;    

@public 
def timer(seconds = 10, show_counter = False):
    for remaining in range(seconds, 0, -1):
        if show_counter:
            sys.stdout.write("\b")
            sys.stdout.write(convert_time(remaining)) 
            sys.stdout.flush()
            sys.stdout.write("\b")
        sleep(1)

@public
def convert_time(time):
    hours, rem = divmod(time, 3600)
    minutes, seconds = divmod(rem, 60)
    return "{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds)

@public
def get_timespan(start,end):
    return convert_time(end-start)

@public
def print_progressbar(iteration, total, prefix='', suffix='', decimals=1, bar_length=100, old_length=0):
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round((bar_length * iteration) / float(total)))
    #bar = '█' * filled_length + '-' * (bar_length - filled_length)
    bar = '#' * filled_length + '-' * (bar_length - filled_length)
    bar_string = '%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)

    if old_length > 0:
        sys.stdout.write('\b' * old_length)

    sys.stdout.write(bar_string)

    sys.stdout.flush()

    return len(bar_string)

def __get_api_result(result):
    if result and result.status_code == 200:     
        try:   
            return result.json(object_hook=__json_object_hook)
        except json.JSONDecodeError as e:
            return result.text

    return None

def __json_object_hook(d):
    d = convert_to_lower_keys(d)
    #if  return_json_results:
    return d
    #return namedtuple('violation', d.keys())(*d.values())

public(public)


