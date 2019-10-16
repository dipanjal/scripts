import wallhavenapi
import argparse


class WallHaven:
    DOWNLOAD_PATH = 'downloads/{search_query}/{id}.{type}'
    API_KEY = "Mv3Gri8rUBbM3b4SA2Eqt3E5moqOcwPT"
    SEARCH_QUERY = None
    TOTAL_DOWNLOAD = 0

    def __init__(self,):
        query = self.argument_parser()
        self.SEARCH_QUERY = query
        print('searching', query, '...')
        wall_haven_api = wallhavenapi.WallhavenApiV1(api_key=None)
        response = wall_haven_api.search(q=query, sorting=wallhavenapi.Sorting.favorites)
        if response:
            last_page = int(response['meta']['last_page'])
            current_page = int(response['meta']['current_page'])
            print('total image found:', response['meta']['total'])
            self.save_image_response(response['data'], wall_haven_api)
            current_page += 1
            for i in range(current_page, last_page):
                response = wall_haven_api.search(q=query, sorting=wallhavenapi.Sorting.favorites, page=i)
                self.save_image_response(response['data'], wall_haven_api)

            print("total downloaded: ", self.TOTAL_DOWNLOAD)
        else:
            print('no wallpaper found')

    def save_image_response(self, data_list, wall_haven_api):
        for data in data_list:
            image_id = data['id']
            image_type = data['file_type'].split('/')[1]
            download_path = self.DOWNLOAD_PATH.format(search_query=self.SEARCH_QUERY, id=image_id, type=image_type)
            path = wall_haven_api.download_walpaper(data['id'], download_path)
            self.TOTAL_DOWNLOAD += 1
            print('[{}]saved in'.format(self.TOTAL_DOWNLOAD), path)

    @staticmethod
    def argument_parser():
        parser = argparse.ArgumentParser(prog='python3 wallhaven.py', usage='%(prog)s [-u|-w]')
        parser.add_argument('-q', '--query', nargs='?', const='query', action='store', type=str, help='search query')
        args = parser.parse_args()

        return args.query


WallHaven()
