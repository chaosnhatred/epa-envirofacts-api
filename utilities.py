# -*- coding: utf-8 -*-

import sys
from time import sleep
from contextlib import contextmanager
from enum import Enum

@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout= sys.stdout
        sys.stdout= devnull
        try:  
            yield
        finally:
            sys.stdout= old_stdout
 
def timer(seconds = 10, show_counter = False):
    for remaining in range(seconds, 0, -1):
        if show_counter:  
            time_str = convert_time(remaining)          
            sys.stdout.write(time_str) 
            sys.stdout.flush()
            sys.stdout.write("\b" * len(time_str))
        sleep(1)

def convert_time(time):
    hours, rem = divmod(time, 3600)
    minutes, seconds = divmod(rem, 60)
    return "{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds)

def get_timespan(start,end):
    return convert_time(end-start)

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

class RestApiResultType(Enum):
    JSON = 'json'
    XML = 'xml'
    CSV = 'csv'


