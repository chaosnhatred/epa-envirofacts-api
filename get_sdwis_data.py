# -*- coding: utf-8 -*-

import csv, os, errno, threading, queue, sys
import EPA.Envirofacts.Configuration as config
import EPA.Envirofacts.SDWIS.Violation as violation
from io import StringIO
from time import sleep
from optparse import OptionParser
from datetime import datetime
#from EPA.Envirofacts.SDWIS import Violation
#from EPA.Envirofacts import Configuration
from EPA.Utilities import suppress_stdout, get_timespan, print_progressbar

def wrapper(func, args, queue):
    try:
        queue.put(func(*args))
    except Exception as e:
        sys.stdout.write('%s\n' % e)
    finally:
        return

def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor

def run_thread(thread, queue, show_spinner=True):
    spinner = spinning_cursor()

    thread.start()
    while thread.isAlive():
        if show_spinner:
            sys.stdout.write(next(spinner))
            sys.stdout.flush()        
            sys.stdout.write('\b')
        sleep(0.25)
    thread.join()    
    return queue.get()

def parse_results(result):
    final_result = []
    v_count = 0
    csv_list = None

    with StringIO(result) as in_s:       
        csv_reader = csv.reader(in_s)        
        csv_list = list(csv_reader)
    
    if not csv_list and len(csv_list) <= 0:
            return None

    #with StringIO() as out_s:                   
    #    csv_writer = csv.writer(out_s, delimiter = ",")
    header = csv_list[0]
    final_result.append(header)
    #csv_writer.writerow(header)
    total = len(csv_list)  
    pbar_length = print_progressbar(v_count, total, bar_length=20, suffix='(%d/%d)' % (v_count, total))
    for w in csv_list:
        v_count += 1            
        if w != header:
            final_result.append(w)
            #csv_writer.writerow(w)        
        pbar_length = print_progressbar(v_count, total, bar_length=20, suffix='(%d/%d) ' % (v_count, total), old_length=pbar_length)
    print_progressbar(v_count, total, bar_length=20, suffix='(%d/%d)' % (v_count, total), old_length=pbar_length)
        #final_result = out_s.getvalue()

    return final_result

def write_results(filename, result):   
    if not filename:
        print('filename cannot be empty or null')
        return
    
    if not result and len(result) > 0:
        return

    try:
        os.remove(filename)
    except OSError as e:
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise

    with open(filename, 'w', newline='') as f:
        #w = csv.DictWriter(f, result[0].keys())
        w = csv.writer(f)
        #w.writeheader()
        w.writerows(result)

def main():
    count = options.max_records
    final_results = []
    q = queue.Queue()
    config.state = options.state
    config.result_format = 'csv'

    print('====== Violations for the state: %s ======' % config.state)
    
    if count <= 0:
        sys.stdout.write('---Getting violation count (step 0/3): ')
        start_time = datetime.now().timestamp()    
        try:
            count = violation.get_count()
        except:
            sys.stdout.write(' [failed]')
        else:
            sys.stdout.write(' [done]')
        end_time = datetime.now().timestamp()
        sys.stdout.write(' [%s]\n' % get_timespan(start_time, end_time))

    sys.stdout.write('---Getting %d violations (step 1/3): ' % count)
    start_time = datetime.now().timestamp()    
    try:
        if count <= 0:
            t = threading.Thread(target=wrapper, args=(violation.get_all, [], q))
        else:
            t = threading.Thread(target=wrapper, args=(violation.get, (count,), q))

        results = run_thread(t, q)    
    except:
        sys.stdout.write(' [failed]')
    else:
        sys.stdout.write(' [done]')
    end_time = datetime.now().timestamp()
    sys.stdout.write(' [%s]\n' % get_timespan(start_time, end_time))
    

    sys.stdout.write('---Parsing results (step 2/3): ')
    start_time = datetime.now().timestamp()
    if results and len(results) > 0:   
        try: 
            t = threading.Thread(target=wrapper, args=(parse_results, (results,), q))
            final_results = run_thread(t, q, False)
        except:
            sys.stdout.write(' [failed]')
        else:
            sys.stdout.write(' [done]')
    else:
        sys.stdout.write(' [skipping]')
    end_time = datetime.now().timestamp()
    sys.stdout.write(' [%s]\n' % get_timespan(start_time, end_time))

    sys.stdout.write('---Saving results to %s (step 3/3): ' % options.filename)
    start_time = datetime.now().timestamp()
    if final_results and len(final_results) > 0:
        try:
            t = threading.Thread(target=wrapper, args=(write_results, (options.filename, final_results,), q))
            run_thread(t, q)
        except:
            sys.stdout.write(' [failed]')
        else:
            sys.stdout.write(' [done]')
    else:
        sys.stdout.write(' [skipping]')
    end_time = datetime.now().timestamp()
    sys.stdout.write(' [%s]\n' % get_timespan(start_time, end_time))    

if __name__ == "__main__":
    try:
        parser = OptionParser()
        parser.add_option("-s", "--state", dest = "state", default = 'DE',
                            help = "state to get violations for")
        parser.add_option("-f", "--file", dest = "filename", default = 'output.csv',
                            help = "write report to FILE", metavar = "FILE")
        parser.add_option("-q", "--quiet",
                            action = "store_false", dest = "verbose", default=True,
                            help = "don't print status messages to stdout")
        parser.add_option("-m", "--max", dest = "max_records", default = 0, type = int,
                            help = "maximum violations to get")

        (options, args) = parser.parse_args()


        script_start_time = datetime.now().timestamp()
        if not options.verbose:
                with suppress_stdout():
                    main()
        else:
            main()
        script_end_time = datetime.now().timestamp()
        sys.stdout.write('\rScript completed in: %s\n' % get_timespan(script_start_time, script_end_time))
    except KeyboardInterrupt:
            print('process interrupted')
    except Exception as e:
        print(e)
    finally:
        sys.exit()
