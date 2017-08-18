import csv, os, errno, threading, queue
from EPA.Envirofacts.SDWIS import Violation
from EPA.Envirofacts.Configuration import get_state, set_state
from sys import stdout
from time import sleep
from optparse import OptionParser

def wrapper(func, args, queue):
    try:
        queue.put(func(*args))
    except Exception as e:
        stdout.write('%s\n' % e)
    finally:
        return

def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor

def run_thread(thread):
    spinner = spinning_cursor()

    t.start()
    while t.isAlive():
        stdout.write(next(spinner))
        stdout.flush()
        sleep(0.2)
        stdout.write('\b')
    t.join()
    stdout.write('done\n')
    return q.get()

def parse_results(result):
    final_result = []
    v_count = 0

    if not result and len(result) > 0:
        return None

    for w in result:
        if not w['violation'] or type(w['violation']) is not list:
            continue

        tmp = {}
        tmp.update(w)
        tmp.pop('violation', None)
                
        for v in w['violation']: 
            if not v or type(v) is not dict:
                continue

            ++v_count                  
            tmp2 = {}
            tmp2.update(v)
            tmp2.pop('geographic_area', None)
            for g in v['geographic_area']:
                if not g or type(g) is not dict:
                    continue

                    tmp2.update(g)

            tmp2.update(tmp)                
            final_result.append(tmp2)

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

    with open(filename, 'w') as f:
        w = csv.DictWriter(f, result[0].keys())
        w.writeheader()
        w.writerows(result)

parser = OptionParser()
parser.add_option("-s", "--state", dest = "state", default = 'DE',
                  help = "state to get violations for")
parser.add_option("-f", "--file", dest = "filename", default = 'output.csv',
                  help = "write report to FILE", metavar = "FILE")
parser.add_option("-q", "--quiet",
                  action = "store_false", dest = "verbose",
                  help = "don't print status messages to stdout")

(options, args) = parser.parse_args()

final_results = []
q = queue.Queue()
set_state(options.state)

if options.verbose:
    f = open(os.devnull, 'w')
    sys.stdout = f

print('====== Violations for the state: %s ======' % get_state())

count = Violation.get_count()
stdout.write('---Getting %d violations (step 1/3): ' % count)
t = threading.Thread(target=wrapper, args=(Violation.get_all, [], q))
results = run_thread(t)

stdout.write('---Parsing results (step 2/3): ')
if results and len(results) > 0:    
    t = threading.Thread(target=wrapper, args=(parse_results, (results,), q))
    final_results = run_thread(t)
else:
    stdout.write('\b skipping\n There were no Violations or result set was null.\n')

stdout.write('---Saving results to %s  (step 3/3): ' % options.filename)
if final_results and len(final_results) > 0:
    t = threading.Thread(target=wrapper, args=(write_results, (options.filename, final_results,), q))
    run_thread(t)
else:
    stdout.write('\b skipping\n There were no Violations or result set was null.\n')
