from urllib.request import urlopen
import urllib.request
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
from functools import wraps
from bs4 import BeautifulSoup
import pyperclip

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

link = open("links.txt","w")
link_list = ""
anime = input("Enter anime name : ")
start = int(input("Enter starting episode : "))
end = int(input("Enter ending episode : "))
print()

url = "http://m2.chia-anime.tv/view/"+ anime + "-" + str(start)

for episode in range(start,end+1):
    print("Parsing Episode " + str(episode) + "...")

    print("Opening URL (" + url + ")...")

    while(True):
        try:
            s = urlopen_with_retry(url).read()
            break
        except:
            print("Connection Timeout...")

    print("Writing to temporary file...")
    f = open("temp.html","w")
    f.write(s.decode("utf-8") )
    f.close()

    print("Opening Firefox...")

    options = Options()
    options.add_argument('-headless')

    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference('permissions.default.image', 2)
    firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')

    driver = webdriver.Firefox(firefox_profile=firefox_profile, firefox_options=options)

    driver.get(r'file:///C:/Users/pradish/PycharmProjects/ChiaAnimieDownloader/temp.html')

    print("Opening BeautifulSoup...")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    links = soup.find('a', string="Download ")

    print("Writing to file...")
    print(links['href'])
    link_list = link_list + links['href'] + "\n"
    link.write(links['href']+"\n")
    link.flush()

    print("Finding next link...")
    next_link = soup.find('a', string="Next")
    url = "http://m2.chia-anime.tv" + next_link['href']

    print()

    driver.close()

link.close()
print("Copying link list to clipboard...")
pyperclip.copy(link_list)
print("\n All Done.")

