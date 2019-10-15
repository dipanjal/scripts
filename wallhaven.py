import wallhavenapi
from pathlib import Path


class WallHaven:
    DOWNLOAD_PATH = 'downloads/{search_query}/{id}.{type}'
    API_KEY = "Mv3Gri8rUBbM3b4SA2Eqt3E5moqOcwPT"

    def __init__(self, query):
        wall_haven_api = wallhavenapi.WallhavenApiV1(api_key=None)
        response = wall_haven_api.search(q=query, sorting=wallhavenapi.Sorting.favorites)
        for data in response['data']:
            image_id = data['id']
            image_type = data['file_type'].split('/')[1]
            download_path = self.DOWNLOAD_PATH.format(search_query=query, id=image_id, type=image_type)
            path = wall_haven_api.download_walpaper(data['id'], download_path)
            print('saved in', path)


WallHaven('cats')
