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

        # if 301 redirect, the baseUrl might change.
        # one example is from http://daily.2ch.net/idolplus/subback.html
        # to https://asahi.2ch.net/idolplus/subback.html
        subbackUrl = r.url or subbackUrl
        baseUrl = subbackUrl.replace('subback.html', '')

        ubody = unicode(r.content, 'shift-jis', 'replace')
        soup = bs(ubody, 'html.parser')
        baseUrl = urlparse.urljoin(baseUrl, soup.find('base')['href'] or '')
        tags = soup.find(id="trad").find_all('a')
        for t in tags:
            key = subIndex.sub("", t.get_text())
            topic[key] = urlparse.urljoin(baseUrl, t['href'])
    except Exception as e:
        print(subbackUrl)
        print(e)
        raise e
    return topic

if __name__ == '__main__':
    for key, url in getTopics("http://daily.2ch.net/idolplus/").iteritems():
        print(key, url)
