# WallHaven Downloader
## Dependensies

#### install pip 3
```sudo apt install pip3```
#### install [beautiful soup 4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#quick-start) <br>
```pip3 install beautifulsoup4```
#### install [requests](https://pypi.org/project/requests/) <br>
```pip3 install requests```

## Usage

search by url
```python
python3 wallhaven.py -u "https://alpha.wallhaven.cc/search?q=id:38424"
```

search by keyword
```python
python3 wallhaven.py -w cats
```
search by keyword with resulation param
```python
python3 wallhaven.py -w cats -r 16x9
```
