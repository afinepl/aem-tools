import requests
import json
import warnings
import os
import urllib
import threading
from datetime import datetime
from queue import Queue
from queue import Empty
from time import sleep
import argparse
import base64

warnings.filterwarnings('ignore', message='Unverified HTTPS request')

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('url', type=str, help='url to AEM site (e.g. https://some-aem.com)')
parser.add_argument('--input', dest='f_input', type=str, default=None,
                    help='input file location with paths which will be added to queue before launch. Default will be "/"')
parser.add_argument('--threads', dest='t_number', type=int, default=5,
                    help='number of concurrent threads')
parser.add_argument('--credentials', dest='credentials', type=str, default=None,
                    help='number of retries if error occurs')
parser.add_argument('--ftype', type=str, dest='ftype', default='nt:file',
                    help='type from json field "type" which will be considered, others will be ignored')
parser.add_argument('--fname', type=str, dest='fname', default='name',
                    help='attribute name from which data should be written to file')
parser.add_argument('--timeout', dest='timeout', type=int, default=8,
                    help='timeout for a request (in seconds)')
                
args = parser.parse_args()

checked_list = []

if args.f_input is not None:
    f = open(args.f_input)
    input_list = f.readlines()
    f.close()
else:
    print("Input list not provided. Starting from '/', but weak results can be expected.")
    input_list = ['/']

qlist = Queue()
[qlist.put(i) for i in input_list if not ':' in i]
output = Queue()
output_file = f'listing-{datetime.now()}.txt'

if args.credentials is not None:
    credentials = base64.b64encode(args.credentials.encode()).decode("utf-8")
    headers = {f'Authorization': 'Basic ' + credentials}
else:
    headers = ''

def run():
    while not qlist.empty():
        directory = qlist.get()
        if '.' in directory.split('/')[-1]:
            directory = os.path.dirname(os.path.abspath(directory))
        if directory in checked_list:
            continue
        checked_list.append(directory)
        directory = directory.strip()
        url = f'{args.url}{directory}.ext.json'
        r = requests.get(url, verify=False, timeout=args.timeout, allow_redirects=False, headers=headers)
        try:
            for j in r.json():
                if j['type'] == args.ftype:
                    found = directory + j[args.fname]
                    qlist.put(found)
                    output.put(found + "\n")
        except json.decoder.JSONDecodeError as JSONDecodeError:
            # print("JSONDecodeError - ignored")
            pass
        except Empty:
            print("QUEUE EMPTY")
            return

def status():
    sleep(args.timeout)
    while not qlist.empty():
        print("Queue size:", qlist.qsize(), sep=' ', end='\r', flush=True)
        sleep(2)

def writer():
    with open(output_file, 'a+') as fo:
        while True:
            try:
                while True:
                    fo.write(output.get(block=True, timeout=5) + "")
            except:
                if qlist.empty() and output.empty():
                    print("End of writing to file")
                    return
    print("End of writing to file")

threads = []
for i in range(args.t_number):
    t = threading.Thread(target=run)
    threads.append(t)
    t.start()

timer = threading.Thread(target=status)
timer.start()

writer = threading.Thread(target=writer)
writer.start()
[t.join() for t in threads]