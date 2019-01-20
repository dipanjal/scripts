from bs4 import BeautifulSoup
import requests
import sys
from pathlib import Path
import argparse
import re
import datetime
import os
from pathlib import Path


# ROOT_URL = 'https://alpha.wallhaven.cc/search?q=models&search_image=&page={page_number}'
ROOT_URL = 'https://alpha.wallhaven.cc/search?q={search_query}&ratios={screen_ration}&page={page_number}'

DOWNLOAD_PATH = '~/Downloads/{script_name}/{search_query}'



# if len(sys.argv) < 2:
#     print("Enter Search Keyword | ex-> models,id:949,tanned etc")
#     sys.exit()
# scriptname = sys.argv[0].replace('.py','')
# query = sys.argv[1] #taking search query arg from cli
# ration = '' 
# if(sys.argv[2:]):
#     ration = sys.argv[2] #taking screen ration arg from cli
scriptname = sys.argv[0].replace('.py','')
file_path_to_save = DOWNLOAD_PATH.format(script_name=scriptname,search_query='{search_query}')

# ROOT_URL = ROOT_URL.format(search_query=query,page_number='{page_number}',screen_ration=ration)
# # print("Search Url:"+ROOT_URL)


def url_regex_type(s, pat=re.compile(r'^(ftp|http|https):\/\/[^ "]+$')):
    if not pat.match(s):
        print('unexpected or invalid url')
        raise argparse.ArgumentTypeError 
    return s
parser = argparse.ArgumentParser(prog='python3 wallhaven.py', usage='%(prog)s [-u|-w]')
group = parser.add_mutually_exclusive_group()
group.add_argument('-u','--url',nargs='?',const='fixed_url',action='store',type=url_regex_type,help='search by \"<fixed_url>\"')
group.add_argument('-w','--keyword',nargs='?',const='keyword',action='store',type=str,help='search by keyword')
parser.add_argument('-r','--ratio',nargs='?',const='ratio',action='store',help='set screen ratio')

args = parser.parse_args()

if args.url:
    ROOT_URL = (args.url)
    print("fixed url: ",args.url)
    start_index = ROOT_URL.find('=')+1
    end_index = ROOT_URL.find('&')
    keyword = ROOT_URL[start_index:end_index].strip()
    if keyword=='':
        keyword = datetime.datetime.today().strftime('%B %d,%Y')
    #     temp_path = fixed_path+keyword
    #     # temp_loc = file_path_to_save.format(search_query=keyword)
    #     # print('temp:'+temp_loc)
    #     # temp_path = Path(temp_loc).expanduser()
    #     count = 0
    #     print(count,":",temp_path)
    #     # while os.path.exists(temp_path):
    #     while (Path(temp_path).expanduser()).exists:
    #         count = count+1
    #         keyword=datetime.datetime.today().strftime('%B %d,%Y')+"("+str(count)+")"
            
    #         # temp_path = temp_path.replace(keyword,'')
    #         # print('temp_path: '+temp_path)
    #         # keyword = re.sub(r"\(\d+\)","("+str(count)+")", keyword)
    #         temp_path = temp_path+keyword
    #         print(count,":",temp_path)
    #         # temp_loc = file_path_to_save.format(search_query=keyword)
    #         # print('temp:'+temp_loc)
    #         # temp_path = 
        
    file_path_to_save = file_path_to_save.format(search_query=keyword)
    path = Path(file_path_to_save).expanduser()
    path.mkdir(parents=True,exist_ok=True)
elif args.keyword:
    print('keyword: ',args.keyword)
    file_path_to_save = file_path_to_save.format(search_query=args.keyword)
    if args.ratio:
        print('ratio: ',args.ratio)
        ROOT_URL = ROOT_URL.format(search_query=args.keyword,page_number='{page_number}',screen_ration=args.ratio)
    else:
        ROOT_URL = ROOT_URL.format(search_query=args.keyword,page_number='{page_number}',screen_ration='')
else:
    print('usage: python3 wallhaven.py -w <keyword>')

print("root url: "+ROOT_URL)
print("file path: "+file_path_to_save)


total_downloaded = 0

def generate_downloadable_image_url(response,session):
    global total_downloaded
    soup = BeautifulSoup(response.text, 'html.parser')
    divs = soup.find_all('figure', attrs={'class': 'thumb'})
    if len(divs) < 1:
        print("No More Image Found Here! ")
        sys.exit()
    else:
        print("Download Path: "+file_path_to_save)
        path = Path(file_path_to_save).expanduser()
        path.mkdir(parents=True,exist_ok=True)
        #irerate the image figures
        for div in divs:
            pass
            wall_id = div['data-wallpaper-id']
            print(wall_id)
            img_response = session.get('https://wallpapers.wallhaven.cc/wallpapers/full/wallhaven-{iid}.jpg'.format(iid=wall_id), stream=True)
            with open(path/Path(wall_id + '.jpg'), 'wb') as f:
                for chunk in img_response.iter_content():
                    if chunk:
                        f.write(chunk)
                total_downloaded+=1

with requests.Session() as session:
    session.headers.update({'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'})
    response = session.get(ROOT_URL.format(page_number=1))
    if response.ok:
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('figure', attrs={'class': 'thumb'})
        
        if len(divs) < 1:
            print("No Image Found!")
            sys.exit()
        
        count = soup.find('h2').text.split("/")[-1].strip()
        print("Total Page Count: "+count)
        for page_number in range(1,int(count)+1):
            current_page_url=ROOT_URL.format(page_number=page_number)
            response = session.get(current_page_url)
            print(current_page_url)
            generate_downloadable_image_url(response,session)
        print("Total Downloaded: ",total_downloaded)

