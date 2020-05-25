# AEM Tools

## `querybuilder.py` - listing files via querybuilder

This tool will make requests similar to `https://some-aem-website.com/bin/querybuilder.json?path=/etc&type=image&nodename=*&p.limit=100&p.offset=0` in order to write directory listing to file. 

### Installation
```
git clone https://github.com/afinepl/aem-tools.git
cd aem-tools
pip3 install -r requirements.txt
```

### Running script with default settings 
```
python3 ./querybuilder.py https://some-aem-website.com
```

### Example of usage with more complex settings

In order to match your requirements, it is recommended to firstly make a manual request, look at the results and decide which options should be changed by using arguments of a script. Especially, types which can change often are `--ftype` and `--extract`. 

```
python3 ./querybuilder.py https://some-aem-website.com --path "/etc" --ftype "nt:file" --tries 1 --step 1000 --extract "jcr:path"
```

### Docs
```
python3 ./querybuilder.py -h

usage: querybuilder.py [-h] [--step STEP] [--tries TRIES] [--extract EXTRACT]
                       [--credentials CREDENTIALS] [--ftype FTYPE]
                       [--path PATH]
                       url

Process some integers.

positional arguments:
  url                   url to AEM site (e.g. https://some-aem.com)

optional arguments:
  -h, --help            show this help message and exit
  --step STEP           number of records retrieved per request
  --tries TRIES         number of retries if error occurs
  --extract EXTRACT     value to extract from returned json (path, jcr:path
                        etc.)
  --credentials CREDENTIALS
                        number of retries if error occurs
  --ftype FTYPE         value of nt:file GET field
  --path PATH           value of path GET field
```
