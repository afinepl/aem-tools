# AEM Tools

## Installation
```
git clone https://github.com/afinepl/aem-tools.git
cd aem-tools
pip3 install -r requirements.txt
```

## `querybuilder.py` - listing files via querybuilder

This tool will make requests similar to `https://some-aem-website.com/bin/querybuilder.json?path=/etc&type=image&nodename=*&p.limit=100&p.offset=0` in order to write directory listing to file. 

### Running script with default settings 
```
python3 querybuilder.py https://some-aem-website.com
```

### Example of usage with more complex settings

In order to match your requirements, it is recommended to firstly make a manual request, look at the results and decide which options should be changed by using arguments of a script. Especially, types which can change often are `--ftype` and `--extract`. 

```
python3 querybuilder.py https://some-aem-website.com --path "/etc" --ftype "nt:file" --tries 1 --step 1000 --extract "jcr:path"
```

### Docs
```
python3 querybuilder.py -h

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

## `ext.json.py` - enumeration using .ext.json added to path

The script will recursively traverse through the files listed by appending `.ext.json` to the end of the url. Providing list of files/directories as a starting point is recommended. The list can be taken from the output of `querybuilder.py`.

Running the script can take many minutes (or even an hour), but results are written to the output file dynamically. 

The script prints out the queue size every few seconds. This number can both grow and shrink, but eventually it will end up with a zero. Variations of this number happen because when new possible paths are found (especially in the beginning), they are added to the queue.

### Running script with recommended settings
```
python3 extjson.py https://some-aem-website.com --input starting-paths.txt
```

`starting-paths.txt` content example:
```
/etc
/content
/content/geometrixx
...
```

### Example of usage with more complex settings
```
python3 extjson.py "https://some-aem-website.com" --input "my-list.txt" --threads 10 --fname "name" --ftype "nt:file"
```

### Docs
```
python3 extjson.py -h

usage: extjson.py [-h] [--input F_INPUT] [--threads T_NUMBER]
                  [--credentials CREDENTIALS] [--ftype FTYPE] [--fname FNAME]
                  [--timeout TIMEOUT]
                  url

Process some integers.

positional arguments:
  url                   url to AEM site (e.g. https://some-aem.com)

optional arguments:
  -h, --help            show this help message and exit
  --input F_INPUT       input file location with paths which will be added to
                        queue before launch. Default will be "/"
  --threads T_NUMBER    number of concurrent threads
  --credentials CREDENTIALS
                        number of retries if error occurs
  --ftype FTYPE         type from json field "type" which will be considered,
                        others will be ignored
  --fname FNAME         attribute name from which data should be written to
                        file
  --timeout TIMEOUT     timeout for a request (in seconds)
```