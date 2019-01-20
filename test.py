from bs4 import BeautifulSoup
import requests
import sys
import os
from os.path import expanduser
from pathlib import Path
import argparse
import re

import datetime

ROOT_URL = 'https://alpha.wallhaven.cc/search?q={search_query}&ratios={screen_ration}&page={page_number}'
USER_HOME = expanduser("~")
FILE_PATH_TO_SAVE = USER_HOME+'/Downloads/wallhaven/'

def getNextFilePath(output_folder):
    highest_num = 0
    for f in os.listdir(output_folder):
        if os.path.isfile(os.path.join(output_folder, f)):
            file_name = os.path.splitext(f)[0]
            try:
                file_num = int(file_name)
                if file_num > highest_num:
                    highest_num = file_num
            except ValueError:
                'The file name "%s" is not an integer. Skipping' % file_name

    output_file = os.path.join(output_folder, str(highest_num + 1))
    return output_file

def url_regex_type(s, pat=re.compile(r'^(ftp|http|https):\/\/[^ "]+$')):
    if not pat.match(s):
        print('unexpected or invalid url')
        raise argparse.ArgumentTypeError 
    return s
parser = argparse.ArgumentParser(prog='python3 wallhaven.py', usage='%(prog)s [-u|-w]')
group = parser.add_mutually_exclusive_group()
group.add_argument('-u','--url',nargs='?',action='store',const='fixed_url',type=url_regex_type,help='search by \"<fixed_url>\"')
group.add_argument('-w','--keyword',nargs='?',const='keyword',action='store',type=str,help='search by keyword')
parser.add_argument('-r','--ratio',nargs='?',const='ratio',action='store',help='set screen ratio')

args = parser.parse_args()

if args.url:
    # print("fixed url: ",args.url)
    ROOT_URL = args.url
    keyword=datetime.datetime.today().strftime('%B %d,%Y')
    generated_file_path = FILE_PATH_TO_SAVE+keyword
    next_file_path = getNextFilePath(generated_file_path)
    print('next_file_path: ',next_file_path)
elif args.keyword:
    print('keyword: ',args.keyword)
    if args.ratio:
        print('ratio: ',args.ratio)
        ROOT_URL = ROOT_URL.format(search_query=args.keyword,page_number='{page_number}',screen_ration=args.ratio)
    else:
        ROOT_URL = ROOT_URL.format(search_query=args.keyword,page_number='{page_number}',screen_ration='')
else:
    print('usage: python3 wallhaven.py -w <keyword>')

print("root url: "+ROOT_URL)

