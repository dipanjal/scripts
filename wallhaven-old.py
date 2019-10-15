import argparse
import datetime
import imghdr
import os
import re
import sys
import time
from pathlib import Path
import json

import requests
from bs4 import BeautifulSoup

# ROOT_URL = 'https://alpha.wallhaven.cc/search?q={search_query}&ratios={screen_ration}&page={page_number}'
ROOT_URL = 'https://wallhaven.cc/search?q={search_query}&ratios={screen_ration}&page={page_number}'
DOWNLOAD_PATH = '~/Downloads/{script_name}/{search_query}'
URL_TYPE = ''
keyword = ''
is_NSFW = False

script_name = sys.argv[0].replace('.py', '')

if '/' in script_name:
    script_name = script_name.split('/')[-1]

file_path_to_save = DOWNLOAD_PATH.format(script_name=script_name, search_query='{search_query}')


# url validation
def url_regex_type(s, pat=re.compile(r'^(ftp|http|https):\/\/[^ "]+$')):
    if not pat.match(s):
        print('unexpected or invalid url')
        raise argparse.ArgumentTypeError
    return s


# image exist or
# if the image is corrupted
def is_image_exist_or_corrupted(image_file):
    if image_file.exists():
        if imghdr.what(image_file.resolve()):
            return True
        os.remove(image_file.resolve())
    return False


# write new file from buffer
def write_image_file(img_response, image_file):
    try:
        with open(image_file, 'wb') as f:
            for chunk in img_response.iter_content():
                if chunk:
                    f.write(chunk)
        return True
    except IOError:
        return False


# write response logs in a json file
def write_response_log(resp):
    log_file_dir = Path('logs/').expanduser()
    log_file_dir.mkdir(parents=True, exist_ok=True)

    date = datetime.datetime.today().strftime("%B %d, %Y")
    log_file_name = date + '-log.json'
    log_file_path = log_file_dir / Path(log_file_name)
    print(log_file_path)
    with open(log_file_path, 'w') as file:
        json.dump(resp, file)


# image downloaded
def download_images_from_current_page(response, session):
    global total_downloaded
    soup = BeautifulSoup(response.text, 'html.parser')
    divs = soup.find_all('figure', attrs={'class': 'thumb'})
    if len(divs) < 1:
        print("No More Image Found Here! ")
        return False
    else:
        directory_path = Path(file_path_to_save).expanduser()
        directory_path.mkdir(parents=True, exist_ok=True)

        # iterate the image figures
        for div in divs:
            wall_id = div['data-wallpaper-id']
            image_file = directory_path / Path(wall_id + '.jpg')
            if not is_image_exist_or_corrupted(image_file):
                # flag = True
                # print('xxx')
                # url_format = 'https://wallpapers.wallhaven.cc/wallpapers/full/wallhaven-{iid}.{ext}'
                id_prefix = wall_id[:2]
                url_format = 'https://w.wallhaven.cc/full/{iid_prefix}/wallhaven-{iid}.{ext}'
                # https://w.wallhaven.cc/full/j8/wallhaven-j8q1xy.jpg
                default_extension = 'jpg'
                while True:
                    try:
                        hd_image_url = url_format.format(iid_prefix=id_prefix, iid=wall_id, ext=default_extension)
                        print(hd_image_url)
                        img_response = session.get(hd_image_url, stream=True, timeout=5)
                        file_size = len(img_response.content) / 2048
                        # file_size_in_kb = str(resp_content_length)+" KB"
                        if img_response.ok:
                            # max image size 1.5 MB
                            if file_size <= 2500:
                                print(wall_id + "." + default_extension + ' (%.2f' % file_size + 'KB)')
                                image_file = directory_path / Path(wall_id + '.' + default_extension)
                                if write_image_file(img_response, image_file):
                                    total_downloaded += 1
                                    default_extension = 'jpg'
                                    break
                            else:
                                print('Too Large ' + wall_id + "." + default_extension + '(%2f' % file_size + ')')
                                break
                        elif img_response.status_code == 404:
                            default_extension = 'png'

                    except Exception as identifier:
                        print(identifier)
                        time.sleep(1)
                        print('trying to reconnect....')
        return True


# tag parser
def parse_tags(request_url):
    with requests.Session() as session:
        session.headers.update({
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'})
        resp = session.get(request_url)
        if resp.ok:
            beautiful_soup = BeautifulSoup(resp.text, 'html.parser')
            tag = beautiful_soup.find('h1', attrs={'class': 'tagname'}).text
            return tag


# taking args from cli
parser = argparse.ArgumentParser(prog='python3 wallhaven-old.py', usage='%(prog)s [-u|-w]')
group = parser.add_mutually_exclusive_group()
group.add_argument('-u', '--url', nargs='?', const='fixed_url', action='store', type=url_regex_type,
                   help='search by \"<fixed_url>\"')
group.add_argument('-w', '--keyword', nargs='?', const='keyword', action='store', type=str, help='search by keyword')
parser.add_argument('-r', '--ratio', nargs='?', const='ratio', action='store', help='set screen ratio')
parser.add_argument('-x', '--nsfw', nargs='?', const='true', action='store', help='unlock nude content')

args = parser.parse_args()

# args handlers
if args.url:
    if '/tag/' in args.url:
        ROOT_URL = args.url
        keyword = parse_tags(ROOT_URL)
        URL_TYPE = 'TAG'
    else:
        ROOT_URL = args.url + '&page={page_number}'
        start_index = args.url.find('=') + 1
        end_index = args.url.find('&')
        keyword = args.url[start_index:end_index].strip()
        if keyword == '':
            keyword = datetime.datetime.today().strftime('%B %d,%Y')

        # extracting NSFW flag from url
        if 'purity=' in args.url:
            purity_bit_mask = re.findall(r'purity=\d{3}', args.url)[0].replace('purity=', '')
            nsfw_bit = purity_bit_mask[2:]
            is_NSFW = True if nsfw_bit is '1' else False

    file_path_to_save = file_path_to_save.format(search_query=keyword)
elif args.keyword:
    keyword = args.keyword
    file_path_to_save = file_path_to_save.format(search_query=args.keyword)
    if args.nsfw:
        is_NSFW = True
    if args.ratio:
        print('ratio: ', args.ratio)
        ROOT_URL = ROOT_URL.format(search_query=args.keyword, page_number='{page_number}', screen_ration=args.ratio)
    else:
        ROOT_URL = str(
            ROOT_URL.format(search_query=args.keyword, page_number='{page_number}', screen_ration='')).replace(
            '&ratios=', '').replace('&screen_ration', '')
else:
    print('usage: python3 wallhaven-old.py -w <keyword>')


def login_wallhaven(session):
    login_page_url = 'https://wallhaven.cc/login'
    login_page = session.get(login_page_url)

    if login_page.ok:
        soup = BeautifulSoup(login_page.text, 'html.parser')
        token = soup.findAll('input', {'name': '_token'})[0]['value']

        payload = {
            '_token': token,
            'username': 'femebobi@next2cloud.info',
            'password': '123456'
        }

        login_post_url = 'https://wallhaven.cc/auth/login'
        response = session.post(login_post_url, data=payload)
        # global is_NSFW
        # if not response.ok:
        #     is_NSFW = False
        return (session, response)


file_path_to_save = file_path_to_save.replace("//", "/")
print("Downloaded Path: " + file_path_to_save)
total_downloaded = 0

with requests.Session() as session:
    session.headers.update({'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                          'Chrome/71.0.3578.98 Safari/537.36'})
    if is_NSFW:
        session, response = login_wallhaven(session)
        if response.ok:
            print("NSFW Content Allowed")

    request_url = ROOT_URL
    if URL_TYPE != 'TAG':
        request_url = ROOT_URL.format(page_number=1)
    try:
        # print(request_url)
        response = session.get(request_url)
        response_log_dict = []

        if response.ok:
            soup = BeautifulSoup(response.text, 'html.parser')
            divs = soup.find_all('figure', attrs={'class': 'thumb'})

            if len(divs) < 1:
                print("No Image Found!")
                sys.exit()
            page_number = 1
            flag = True
            while flag:
                current_page_url = ROOT_URL

                if URL_TYPE != 'TAG':
                    current_page_url = ROOT_URL.format(page_number=page_number)

                # dumping page
                response = session.get(current_page_url)
                print('Downloading From: ', current_page_url)
                # responseLogs['url'] = current_page_url
                log_dict = {
                    'response': response.status_code,
                    'method': 'get',
                    'url': current_page_url,
                    'keyword': keyword,
                    'datetime': datetime.datetime.today().strftime("%I:%M%p %B %d, %Y")
                }
                response_log_dict.append(log_dict)
                # write_response_log(responseLogs)
                flag = download_images_from_current_page(response, session)
                page_number += 1

                if URL_TYPE == 'TAG':
                    flag = False

            print("Total Downloaded: ", total_downloaded)
            write_response_log(response_log_dict)
    except Exception as ex:
        print(ex)
        pass
