# TDictionary
TDictionary is a simple command line tool to look up an English word and find its Chinese meanings.

The dictionaries are web based, including the following so far,
  - A simple dictionary
  - A Collins dictionary

### Installation
The script is written in Python in a compatiable way, so both the latest Python 2 and Python 3 should work.

Install the Python packages by running
```sh
$ pip install -r requirements.txt
```

### Usage
To check the help message
```sh
$ ./t_dictionary.py --help
```

## Examples
The default behaviour is to print the simple meanings and two items from Collins to quickly understand the word.
```sh
$ ./t_dictionary.py pretty
```

To show all the items from Collins to quickly understand the word.
```sh
$ ./t_dictionary.py -a pretty
$ ./t_dictionary.py --all-collins-items pretty
```

To specify the number of items to show from Collins to quickly understand the word.
```sh
$ ./t_dictionary.py -c 10 there
$ ./t_dictionary.py --collins-count 10 there
```
