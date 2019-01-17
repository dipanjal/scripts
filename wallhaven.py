from bs4 import BeautifulSoup
import requests
import re

ROOT_URL = 'https://alpha.wallhaven.cc/search?q=models&search_image='

with requests.Session() as session:
    session.headers.update({'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'})
    response = session.get(ROOT_URL)
    if response.ok:
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('figure', attrs={'class': 'thumb'})
        for div in divs:
            wall_id = div['data-wallpaper-id']
            print(wall_id)

            img_response = session.get('https://wallpapers.wallhaven.cc/wallpapers/full/wallhaven-{iid}.jpg'.format(iid=wall_id), stream=True)
            with open(wall_id + '.jpg', 'wb') as f:
                for chunk in img_response.iter_content():
                    if chunk:
                        f.write(chunk)
