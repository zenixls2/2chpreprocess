import dumpMenu
import subback
import os.path
import urlparse
import cPickle
import argparse
import time
import sqlite3
from multiprocessing import Pool
from process import process

conn = sqlite3.connect('./save/output.db')

BOARD_TOPIC_PATH = "./save/boardTopic.pkl"
CHECK_POINT_PATH = "./save/checkpoint.pkl"


def processMenuToGetTopicLinks(rerun=False):
    menu = None
    if not rerun and os.path.isfile(dumpMenu.MENU_PATH):
        menu = dumpMenu.loadMenu()
    else:
        menu = dumpMenu.getMenu()
    function_boards = [
        'http://www.2ch.net/',
        'http://info.2ch.net/',
        'http://search.2ch.net/',
        'http://dig.2ch.net/',
        'http://stat.2ch.net/',
        'http://o.8ch.net/',
        'http://i.2ch.net/',
        'http://www.2ch.net/kakolog.html',
        'http://notice.2ch.net/',
        'http://jp.8ch.net/'
        'http://headline.2ch.net/bbynamazu/',
        'http://headline.2ch.net/bbypinkH0/',
        'http://info.2ch.net/wiki/',
        'http://info.2ch.net/?curid=2078',
        "http://premium.2ch.net/",
        'http://qb5.2ch.net/saku2ch/',
        'mailto:2ch@2ch.net',
        'http://be.2ch.net/',
        'http://newsnavi.2ch.net/'
    ]
    print("Total %d catgories" % len(menu.keys()))
    boardTopics = {}
    if not rerun and os.path.isfile(BOARD_TOPIC_PATH):
        with open(BOARD_TOPIC_PATH, 'rb') as f:
            print("read records")
            boardTopics = cPickle.load(f)
    else:
        for name, url in menu.iteritems():
            if url in function_boards:
                continue
            topic = {}
            u = urlparse.urlparse(url)
            if u.path.startswith('/bby'):
                pass
            elif u.netloc.endswith('2ch.net') and u.netloc != 'mevius.2ch.net':
                topic = subback.getTopics(url)
            elif u.netloc.endswith('bbspink.com'):
                pass
            boardTopics[name] = topic
            print(name + " parsing done, %d records" % len(topic.keys()))
        with open(BOARD_TOPIC_PATH, 'wb') as f:
            cPickle.dump(boardTopics, f, cPickle.HIGHEST_PROTOCOL)
    print("Total %d topics" % sum(map(
                        lambda x: len(boardTopics[x]), boardTopics)))


# TODO: save file to dist
def processTopicLinksToGetDialogs(rerun=False, maxParallel=2):
    boardTopics = {}
    if not os.path.isfile(BOARD_TOPIC_PATH):
        print("Please run with -t first to generate topic links")
        return
    with open(BOARD_TOPIC_PATH, 'rb') as f:
        boardTopics = cPickle.load(f)

    workers = 0
    checkpoint = 0

    if not rerun and os.path.isfile(CHECK_POINT_PATH):
        with open(CHECK_POINT_PATH, 'rb') as f:
            checkpoint = cPickle.load(f)
    print(checkpoint)

    index = 0
    pool = Pool(maxParallel)

    workersList = [None] * maxParallel

    c = conn.cursor()

    c.execute(("create table if not exists messages ("
               "name unicode,"
               "id int,"
               "thread_id text,"
               "message text,"
               "primary key (id, name, thread_id)"
               ")"))

    for name, urlmap in boardTopics.iteritems():
        for key, url in urlmap.iteritems():
            if index <= checkpoint:
                index += 1
                continue
            print("Processing %s: %s" % (key, url))
            workers += 1
            result = pool.apply_async(process, (index, url, name,))
            index += 1
            tf = True
            while workers > maxParallel:
                time.sleep(3)
                for i, j in enumerate(workersList):
                    if j and j.ready():
                        data = j.get()
                        for d in data:
                            try:
                                c.execute(
                                    "INSERT INTO messages values (?,?,?,?)",
                                    (d.name, d.id, d.thread_id, d.message,))
                            except sqlite3.IntegrityError as e:
                                print(e)
                                pass
                        if tf:
                            workersList[i] = result
                            tf = False
                        else:
                            workersList[i] = None
                        workers -= 1
            if tf:
                for i, j in enumerate(workersList):
                    if not j:
                        workersList[i] = result
                        break
            conn.commit()
            with open(CHECK_POINT_PATH, 'wb') as f:
                cPickle.dump(index, f, cPickle.HIGHEST_PROTOCOL)
    pool.join()
    for i in workersList:
        data = i.get()
        for d in data:
            conn.execute("INSERT INTO messages values (?,?,?,?)", (
                d.name, d.id, d.thread_id, d.message))
    c.commit()
    c.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                        description="2ch data preprocessor & crawler")
    parser.add_argument('-t', '--topic', help="get topic links",
                        action='store_true')
    parser.add_argument('-r', '--rerun', help="ignore cache results and rerun",
                        action='store_true')
    parser.add_argument('-p', '--process', help="process generated topic link",
                        action='store_true')
    parser.add_argument('-w', '--worker', type=int, help="number of workers",
                        default=3)
    args = parser.parse_args()
    print(args)
    if args.topic:
        processMenuToGetTopicLinks(args.rerun)
    if args.process:
        processTopicLinksToGetDialogs(args.rerun, args.worker)
