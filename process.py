import requests
import re
from datetime import datetime
from dateutil.parser import parse
from bs4 import BeautifulSoup as bs

subweekdays = re.compile(r"\(.+\)")
subId = re.compile(r"ID:.+")
matchTimestamp = re.compile(r"\d+/\d+/\d+ \d+:\d+:\d+\.\d+")
originTime = datetime(1970, 1, 1)


class Message(object):
    def __init__(self, name, id, thread_id, t, m):
        self.name = name
        self.id = id
        self.thread_id = thread_id
        self.timestamp = t
        self.message = m


class Dummy(object):
    def get_text(self):
        return ''


dummy = Dummy()


def process(index, url, name):
    url = url.replace('/l50', '')
    thread_id = url.split('/')[-1].strip()
    r = None
    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError as e:
        print(e)
        return []

    if r.status_code != 200 and r.status_code != 204:
        print("index %d, %s get fail: %d" % (index, url, r.status_code))
        return []
    ubody = unicode(r.content, 'shift-jis', 'replace')
    soup = bs(ubody, 'html5lib')
    tags = []
    try:
        tags = soup.find(class_='thread').find_all(class_="post")
    except Exception as e:
        print(e)
        print(url)
        pass
    result = [None] * len(tags)
    for t in tags:
        dtstring = subId.sub("", subweekdays.sub(
                        "", (t.find(class_='date') or dummy).get_text()))

        id = int(t['id'])

        timestamp = None
        if dtstring:
            matchResult = matchTimestamp.match(dtstring)
            if matchResult:
                try:
                    dt = parse(matchResult.group(0))
                    timestamp = (dt-originTime).total_seconds()
                except Exception as e:
                    print(url)
                    print(dtstring)
                    # some errr str is like 2006/03/32(土) 18:13:35.00
                    # we are unable to parse it here
            elif id >= 2:
                timestamp = result[id-2].timestamp

        message = t.find(class_="message").get_text() \
                   .replace('\n', '').replace('\r', '').strip()
        result[id-1] = Message(name, id, thread_id, timestamp, message)
    return result


if __name__ == '__main__':
    result = process(
            0, "http://lavender.2ch.net/test/read.cgi/hobby/1112706898/l50")
    for i in result:
        print(i.id, i.timestamp, i.message)
