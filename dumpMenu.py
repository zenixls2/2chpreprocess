from bs4 import BeautifulSoup as bs
import requests
import cPickle

MENU_URL = "http://menu.2ch.net/bbstable.html"
MENU_PATH = "./save/menu.pkl"

def getMenu(save=True):
    r = requests.get(MENU_URL)
    if r.status_code != 200 and r.status_code != 204:
        raise Exception('connect to menu fail: ' + str(r.status_code))
    ubody = unicode(r.content, 'shift-jis', 'replace')
    menu = {}
    soup = bs(ubody, 'html.parser')
    tags = soup.find_all('a')
    for t in tags:
        menu[t.get_text()] = t['href']
    if save:
        with open(MENU_PATH, 'wb') as f:
            cPickle.dump(menu, f, cPickle.HIGHEST_PROTOCOL)
    return menu

def loadMenu():
    with open(MENU_PATH, 'rb') as f:
        menu = cPickle.load(f)
        return menu
    return None

if __name__ == '__main__':
    getMenu()
