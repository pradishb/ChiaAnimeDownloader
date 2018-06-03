import urllib.request
import time
from functools import wraps
from bs4 import BeautifulSoup
import pyperclip
import js2py
import re

def retry(tries=4, delay=3, backoff=2, logger=None):
    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except:
                    msg = "Retrying in %d seconds..." % (mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry

@retry(tries=4, delay=3, backoff=2)
def urlopen_with_retry(url):
    return urllib.request.urlopen(url, timeout=10)

def string_from_url(url):
    while (True):
        try:
            s = urlopen_with_retry(url).read()
            return s
        except:
            print("Connection Timeout...")


link = open("links.txt","w")
link_list = ""
anime = input("Enter anime name : ")

print("Searching for anime...")

s = string_from_url("http://m2.chia-anime.tv/catlist.php?tags=" + anime)

soup = BeautifulSoup(s, "html.parser")
search_result = soup.find_all('div', {"class" : "title"})

[print(str(i) + ". " + anime.text) for i, anime in enumerate(search_result)]

choose = int(input("Choose the anime : "))
start = int(input("Enter starting episode : "))
end = int(input("Enter ending episode : "))
print()

anime_url = "http://m2.chia-anime.tv" + search_result[choose].find('a')['href']

print("Opening URL (" + anime_url + ")...")
s = string_from_url(anime_url)

print("Getting anime episode list...")
soup = BeautifulSoup(s, "html.parser")
anime_list = soup.find_all('option')

episode_list = {}

for num, st in enumerate(anime_list):
    numbers = [int(s) for s in st['value'].split('-') if s.isdigit()]
    for episode in numbers:
        episode_list[episode] = num

print()

pa = open("pa.js", "r")
pasc = pa.read()
pa.close()

for episode in range(start,end+1):
    print("Parsing Episode " + str(episode) + "...")

    url = "http://m2.chia-anime.tv/view/" + anime_list[episode_list[episode]]['value']
    print("Opening URL (" + url + ")...")

    s = string_from_url(url)

    soup = BeautifulSoup(s, 'html.parser')
    scripts = soup.find_all('script')
    for script in scripts:
        if "document|" in script.text:
            video_id = re.findall('[0-9a-zA-Z]{60,200}',script.text)

            context = js2py.EvalJs()

            sc = "var ved=re(\"" + video_id[0] + "\",t);" \
                 "var od=vsd.d(''+ved+'');" \
                 "var sed=re(\"\"+od+\"\",e);"

            context.execute(pasc + sc)
            download_link = context.sed.split('\0', 1)[0] + "?download=yes&title=" + search_result[choose].text.replace(' ', '-') + "-Episode-" + str(episode) + ".mp4"

            print("Download Link : " + download_link)
            print()

            link_list = link_list + download_link + "\n"
            link.write(link_list + "\n")
            link.flush()

link.close()
print("Copying link list to clipboard...")
pyperclip.copy(link_list)
print("\nAll Done.")

