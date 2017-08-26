# -*- coding: utf-8 -*-

import csv, os, errno, threading, queue, sys
import EPA.Envirofacts.Configuration as config
import EPA.Envirofacts.SDWIS.Violation as violation
import EPA.Envirofacts.SDWIS.WaterSystem as water_system
from time import sleep
from optparse import OptionParser
from datetime import datetime
from utilities import suppress_stdout, get_timespan, print_progressbar, RestApiResultType

def wrapper(func, args, queue):
        try:
            queue.put(func(*args))
        except Exception as e:
            queue.put(e)
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
    r = queue.get()
    if isinstance(r, Exception):
        raise r

    return r

def parse_results(result, water_system = True):
    final_result = []
    v_count = 0
    csv_list = result
    agency_header = 'water_system.primacy_agency_code'

    if not water_system:
        agency_header = 'violation.primacy_agency_code'
    
    if not csv_list and len(csv_list) <= 0:
            return None

    total = len(csv_list)  
    pbar_length = print_progressbar(v_count, total, bar_length=20, suffix='(%d/%d)' % (v_count, total))
    for w in csv_list:
        v_count += 1    
                
        #Put any post processing logic here        
        if w[agency_header] == config.state.lower():
            final_result.append(w)  
     
        pbar_length = print_progressbar(v_count, total, bar_length=20, suffix='(%d/%d) ' % (v_count, total), old_length=pbar_length)
    print_progressbar(v_count, total, bar_length=20, suffix='(%d/%d)' % (v_count, total), old_length=pbar_length)

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
        w = csv.DictWriter(f, result[0].keys())
        #w = csv.writer(f)        
        w.writeheader()
        w.writerows(result)

def main():
    system_count = 0
    count = options.max_records
    system_results = []
    results = []
    current_step = 1
    q = queue.Queue()
    config.state = options.state
    config.result_format = RestApiResultType.CSV

    print('====== Water safety violations for the state: %s ======' % config.state_fullname)
    
    if not options.v_only:
        sys.stdout.write('---Getting water system count (step %d/%d): ' % (current_step, script_steps))
        start_time = datetime.now().timestamp()    
        try:
            t = threading.Thread(target=wrapper, args=(water_system.get_count_by_state, [], q))
            system_count = run_thread(t, q)
        except Exception as e:
            sys.stdout.write(' [failed]  [Exception: %s] ' % e)
            system_count = 0
        else:
            sys.stdout.write(' [done]')
        end_time = datetime.now().timestamp()
        sys.stdout.write(' [%s]\n' % get_timespan(start_time, end_time))
        current_step = current_step + 1   
    
        sys.stdout.write('---Getting %d water systems (step %d/%d): ' % (system_count, current_step, script_steps))
        start_time = datetime.now().timestamp()    
        try:
            t = threading.Thread(target=wrapper, args=(water_system.get_by_state, [], q))
            system_results = run_thread(t, q)
        except Exception as e:
            sys.stdout.write(' [failed]  [Exception: %s] ' % e)
            system_results = []
        else:
            sys.stdout.write(' [done]')
        end_time = datetime.now().timestamp()
        sys.stdout.write(' [%s]\n' % get_timespan(start_time, end_time))
        current_step = current_step + 1   

    if get_all_violations:
        sys.stdout.write('---Getting violation count (step %d/%d): ' % (current_step, script_steps))
        start_time = datetime.now().timestamp()    
        try:
            t = threading.Thread(target=wrapper, args=(violation.get_count_by_state, [], q))
            count = run_thread(t, q)
        except Exception as e:
            sys.stdout.write(' [failed]  [Exception: %s] ' % e)
            count = 0
        else:
            sys.stdout.write(' [done]')
        end_time = datetime.now().timestamp()
        sys.stdout.write(' [%s]\n' % get_timespan(start_time, end_time))
        current_step = current_step + 1

    sys.stdout.write('---Getting %d violations (step %d/%d): ' % (count, current_step, script_steps))
    start_time = datetime.now().timestamp()        
    try:
        if get_all_violations:
            if options.v_only:
                t = threading.Thread(target=wrapper, args=(violation.get_by_state, [], q))
                results = run_thread(t, q) 
            else:
                if system_results and len(system_results) > 0:
                    s_count = 0
                    pbar_length = print_progressbar(s_count, system_count, bar_length=20, suffix='(%d/%d)' % (s_count, system_count))
                    for s in system_results:
                        s_count += 1
                        t = threading.Thread(target=wrapper, args=(violation.get_by_water_system, (s['water_system.pwsid'],), q))
                        r = run_thread(t, q, False)
                        if r and len(r) > 0:
                            results += r
                        pbar_length = print_progressbar(s_count, system_count, bar_length=20, suffix='(%d/%d)' % (s_count, system_count), old_length=pbar_length)
                    print_progressbar(s_count, system_count, bar_length=20, suffix='(%d/%d)' % (s_count, system_count), old_length=pbar_length)
                else:
                    sys.stdout.write(' [skipping]')
        else:
            t = threading.Thread(target=wrapper, args=(violation.get_by_state, (config.state, count,), q))
            results = run_thread(t, q)    
    except Exception as e:
        sys.stdout.write(' [failed]  [Exception: %s] ' % e)
        results = []
    else:
        sys.stdout.write(' [done]')
    end_time = datetime.now().timestamp()
    sys.stdout.write(' [%s]\n' % get_timespan(start_time, end_time))
    current_step = current_step + 1
    
    if not options.v_only:
        sys.stdout.write('---Parsing water system results (step %d/%d): ' % (current_step, script_steps))
        start_time = datetime.now().timestamp()
        final_system_results = []
        if system_results and len(system_results) > 0:           
            try: 
                t = threading.Thread(target=wrapper, args=(parse_results, (system_results,), q))
                final_system_results = run_thread(t, q, False)
            except Exception as e:
                sys.stdout.write(' [failed]  [Exception: %s] ' % e)
                final_system_results = []
            else:
                sys.stdout.write(' [done]')
        else:
            sys.stdout.write(' [skipping]')
        end_time = datetime.now().timestamp()
        sys.stdout.write(' [%s]\n' % get_timespan(start_time, end_time))
        current_step = current_step + 1
    
    sys.stdout.write('---Parsing violation results (step %d/%d): ' % (current_step, script_steps))
    start_time = datetime.now().timestamp()
    final_results = []
    if results and len(results) > 0:   
        try: 
            t = threading.Thread(target=wrapper, args=(parse_results, (results, False,), q))
            final_results = run_thread(t, q, False)
        except Exception as e:
            sys.stdout.write(' [failed]  [Exception: %s] ' % e)
            final_results = []
        else:
            sys.stdout.write(' [done]')
    else:
        sys.stdout.write(' [skipping]')
    end_time = datetime.now().timestamp()
    sys.stdout.write(' [%s]\n' % get_timespan(start_time, end_time))
    current_step = current_step + 1

    if not options.v_only:
        sys.stdout.write('---Saving water system results to %s(step %d/%d): ' % (system_filename, current_step, script_steps))
        start_time = datetime.now().timestamp()
        if final_system_results and len(final_system_results) > 0:
            try:
                t = threading.Thread(target=wrapper, args=(write_results, (system_filename, final_system_results,), q))
                run_thread(t, q)
            except Exception as e:
                sys.stdout.write(' [failed]  [Exception: %s] ' % e)
            else:
                sys.stdout.write(' [done]')
        else:
            sys.stdout.write(' [skipping]')
        end_time = datetime.now().timestamp()
        sys.stdout.write(' [%s]\n' % get_timespan(start_time, end_time)) 

    sys.stdout.write('---Saving violation results to %s (step %d/%d): ' % (violation_filename, current_step, script_steps))
    start_time = datetime.now().timestamp()
    if final_results and len(final_results) > 0:
        try:
            t = threading.Thread(target=wrapper, args=(write_results, (violation_filename, final_results,), q))
            run_thread(t, q)
        except Exception as e:
            sys.stdout.write(' [failed]  [Exception: %s] ' % e)
        else:
            sys.stdout.write(' [done]')
    else:
        sys.stdout.write(' [skipping]')
    end_time = datetime.now().timestamp()
    sys.stdout.write(' [%s]\n' % get_timespan(start_time, end_time))    

script_steps = 8
system_filename = 'watersystems.csv'
violation_filename = 'violations.csv'
get_all_violations = True
if __name__ == "__main__":
    try:
        parser = OptionParser()
        parser.add_option("-s", "--state", dest = "state", default = 'DE',
                            help = "state to get violations for (2 letter abbreviation. ie . de, pa, ca, tx, etc.")
        parser.add_option("-q", "--quiet",
                            action = "store_false", dest = "verbose", default = True,
                            help = "don't print status messages to stdout")
        parser.add_option("-m", "--max", dest = "max_records", default = 10, type = int,
                            help = "maximum violations to get")
        parser.add_option("-V", "--violations-only", action = "store_true", dest = "v_only", default = False,
                            help = "get violations only")

        (options, args) = parser.parse_args()

        if options.max_records > 0:
            script_steps = script_steps - 1
            get_all_violations = False

        if options.v_only:
            script_steps = script_steps - 4

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
