from bs4 import BeautifulSoup
import requests
import sys

from pathlib import Path


# ROOT_URL = 'https://alpha.wallhaven.cc/search?q=models&search_image=&page={page_number}'
ROOT_URL = 'https://alpha.wallhaven.cc/search?q={search_query}&ratios={screen_ration}&page={page_number}'
# DOWNLOAD_PATH = '~/.config/variety/Downloaded/wallhaven_alpha_wallhaven_cc_search_q_women'
DOWNLOAD_PATH = '~/Downloads/{script_name}/{search_query}'



if len(sys.argv) < 2:
    print("Enter Search Keyword | ex-> models,id:949,tanned etc")
    sys.exit()
scriptname = sys.argv[0].replace('.py','')
query = sys.argv[1] #taking search query arg from cli
ration = '' 
if(sys.argv[2:]):
    ration = sys.argv[2] #taking screen ration arg from cli

file_path_to_save = DOWNLOAD_PATH.format(search_query=query,script_name=scriptname)

# file_path_to_save = DOWNLOAD_PATH


# ROOT_URL = ROOT_URL.format(search_query=query,screen_ration='16x9',page_number='{page_number}')
ROOT_URL = ROOT_URL.format(search_query=query,page_number='{page_number}',screen_ration=ration)
# print("Search Url:"+ROOT_URL)

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

