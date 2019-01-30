#please use with singapore ip address#

from bs4 import BeautifulSoup
import requests

url = "https://www.google.com/search?sa=X&biw=1366&bih=696&q=offices+in+nikunja+2&npsic=0&rflfq=1&rlha=0&rllag=23834098,90417333,241&tbm=lcl#rlfi=hd:;si:;mv:!1m2!1d23.8367516!2d90.41950320000001!2m2!1d23.8272765!2d90.4177248;start:20;tbs:lrf:!2m1!1e2!2m1!1e3!2m1!1e16!2m7!1e17!4m2!17m1!1e2!5m2!17m1!1e2!3sIAE,lf:1,lf_ui:2"
with requests.Session() as session:
    session.headers.update({'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'})
    response = session.get(url)

    if response.ok:
        soup = BeautifulSoup(response.text,'html.parser')
        divs = soup.find_all('div',attrs={'class':'cXedhc'})
        print('found: ',len(divs))
        with open('office_in_nikunjo.csv','w') as csv_file:
            for div in divs:
                office_name = div.find('div',attrs={'class':'dbg0pd'})
                phone = div.select_one('div > span > div:nth-child(3) > span')
                address = div.select_one('div > span > div:nth-child(2) > span:nth-child(1)')
                
                if address and phone:
                    text_line = '"{office_name}", "{address}", "{phone}"\n'
                    line = text_line.format(office_name=office_name.text,address=address.text,phone=phone.text)
                    csv_file.write(line)
                    print(office_name.text+", "+address.text+", "+phone.text)

    else:
        print(response.status_code)