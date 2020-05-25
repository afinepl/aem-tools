import requests
import json
from datetime import datetime
import warnings
import sys
import base64
import argparse

warnings.filterwarnings('ignore', message='Unverified HTTPS request')

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('url', type=str, help='url to AEM site (e.g. https://some-aem.com)')
parser.add_argument('--step', dest='step', type=int, default=4000,
                    help='number of records retrieved per request')
parser.add_argument('--tries', dest='tries', type=int, default=3,
                    help='number of retries if error occurs')
parser.add_argument('--extract', type=str, dest='extract', default='path',
                    help='value to extract from returned json (path, jcr:path etc.)')
parser.add_argument('--credentials', dest='credentials', type=str, default=None,
                    help='number of retries if error occurs')
parser.add_argument('--ftype', type=str, dest='ftype', default='nt:file',
                    help='value of nt:file GET field')
parser.add_argument('--path', type=str, dest='path', default='/',
                    help='value of path GET field')
                
args = parser.parse_args()

def extract_values(obj, key):
    arr = []

    def extract(obj, arr, key):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    results = extract(obj, arr, key)
    return results


def append_list_to_file(lst, output_file):
    output_file = open(output_file, 'a+')
    output_file.write('\n'.join(lst))
    output_file.close()


offset = -args.step
output_file = f'listing-querybuilder-{datetime.now()}.txt'
if args.credentials is not None:
    credentials = base64.b64encode(args.credentials.encode()).decode("utf-8")
    headers = {f'Authorization': 'Basic ' + credentials}
else:
    headers = ''

print("Example request:", f'{args.url}/bin/querybuilder.json?path={args.path}&type={args.ftype}&nodename=*&p.limit={args.step}&p.offset=0')

while True:
    offset += args.step
    print(offset)
    reset = 0
    while True:
        try:
            r = requests.get(
                f'{args.url}/bin/querybuilder.json?path={args.path}&type={args.ftype}&nodename=*&p.limit={args.step}&p.offset={offset}', verify=False, timeout=30, headers=headers)
            if r.status_code != 200:
                raise ConnectionError
            js = r.json()
            lst = extract_values(js, args.extract)
            if len(lst) == 0:
                if offset == 0:
                    print("No results extracted - try other --extract argument or different --path")
                print("DONE - saved in", output_file)
                sys.exit(0)
            append_list_to_file(lst, output_file)
            break
        except json.decoder.JSONDecodeError as e:
            if reset < args.tries:
                print(f"[{offset}] JSONDecodeError - try {reset+1}/{args.tries}")
                reset += 1
            else:
                print(f"[{offset}] JSONDecodeError - did not recover, ignore")
                break
        except ConnectionError:
            if reset < args.tries:
                print(f"[{offset}] Return code != 200 - try {reset+1}/{args.tries}")
                reset += 1
            else:
                print(f"[{offset}] Return code != 200 - did not recover, ignore")
                break
