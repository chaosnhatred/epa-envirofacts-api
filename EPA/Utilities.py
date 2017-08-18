import re, requests
from sys import stdout, modules
from time import sleep
from collections import namedtuple

def public(f):
    """"Use a decorator to avoid retyping function/class names.

    * Based on an idea by Duncan Booth:
    http://groups.google.com/group/comp.lang.python/msg/11cbb03e09611b8a
    * Improved via a suggestion by Dave Angel:
    http://groups.google.com/group/comp.lang.python/msg/3d400fb22d8a42e1
    """
    all = modules[f.__module__].__dict__.setdefault('__all__', [])
    if f.__name__ not in all:  # Prevent duplicates if run from an IDE.
        all.append(f.__name__)
    return f

@public
def convert_to_lower_keys(d):
    if isinstance(d, list):
        return [convert_to_lower_keys(v) for v in d]
    elif isinstance(d, dict):
        return dict((k.lower(), convert_to_lower_keys(v)) for k, v in d.items())
    else:
        return d

@public
def call_rest_api(request, timeout_limit=120):
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
                stdout.write('\ba timeout occurred making the api request: %s' % request)
            timer(60)
            timeout_limit += 120            
        except requests.exceptions.HTTPError as e:
            if p4.match(str(e.response.status_code)):
                if attempt == retries:
                    stdout.write('\burl for was not found for request: %s' % request)
                timer()
                continue
            elif p5.match(str(e.response.status_code)):
                if attempt == retries:
                    stdout.write('\ba server error occurred making the api request: %s' % request)
                timer(120)
                timeout_limit += 120
                continue
            print(e)
            break
        except requests.exceptions.RequestException as e:
            print(e)
            break;    

@public 
def timer(seconds = 10, show_counter = False):
    for remaining in range(seconds, 0, -1):
        if show_counter:
            stdout.write("\b")
            stdout.write("{:2d} seconds".format(remaining)) 
            stdout.flush()
            stdout.write("\b")
        sleep(1)
 
def __get_api_result(result):
    if result and result.status_code == 200:
        return result.json(object_hook=__json_object_hook)

    return None

def __json_object_hook(d):
    d = convert_to_lower_keys(d)
    #if  return_json_results:
    return d
    #return namedtuple('violation', d.keys())(*d.values())

public(public)


