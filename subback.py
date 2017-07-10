import requests
import urlparse
import re
from bs4 import BeautifulSoup as bs

subIndex = re.compile(r"^\d+: ")

def getTopics(baseUrl):
    subbackUrl = urlparse.urljoin(baseUrl, 'subback.html')
    topic = {}
    try:
        r = requests.get(subbackUrl)
        if r.status_code != 200 and r.status_code != 204:
            raise Exception("connection fail for getting topic summary: " +
                            str(r.status_code) + " " +
                            subbackUrl)
        ubody = unicode(r.content, 'shift-jis', 'replace')
        soup = bs(ubody, 'html.parser')
        baseUrl = urlparse.urljoin(baseUrl, soup.find('base')['href'] or '')
        tags = soup.find(id="trad").find_all('a')
        for t in tags:
            key = subIndex.sub("", t.get_text())
            topic[key] = urlparse.urljoin(baseUrl, t['href'])
    except Exception as e:
        print subbackUrl
        print e
    return topic
