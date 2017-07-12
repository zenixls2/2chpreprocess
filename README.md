## 2ch preprocessor
------------------
This is a 2ch crawler & preprocessor for creating chatbot-rnn readable format.
The crawler part is almost complete, but the preprocessor part is still under development.
- TODO ITEMS:
  * Normalize kanji, hirakana and katakana to romaji (alphabet) to decrease the vocabulary amount.
  * truncate useless ANSI Art
  * create a post processor to convert romaji to kanji, hirakana, or katakana
  * preprocess data as dialog format defined in chatbot-rnn

### Features
- Ignore some functional boards, and crawl through all the threads in 2ch
- checkpoint recovery (known bug for ignoring running processes)
- multiple workers for crawling
- save to sqlite db

### Installation
```bash
# Ubuntu
sudo apt-get install sqlite3
# Mac
brew install sqlite3

git clone https://github.com/zenixls2/2chpreprocess
cd 2chpreprocess
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Execution
usage: main.py [-h] [-t] [-r] [-p] [-w WORKER]

2ch data preprocessor & crawler

optional arguments:
  * -h, --help            show this help message and exit
  * -t, --topic           get topic links
  * -r, --rerun           ignore cache results and rerun
  * -p, --process         process generated topic link
  * -w WORKER, --worker WORKER
                          number of workers

First crawl out all topics:
```bash
source venv/bin/activate
python main.py -t
```

And crawl through all threads:
```bash
source venv/bin/activate
python main.py -p -w ${WORKER}
```
Notice that this could stop at any time.
The result is by default save in `save` directory.
You could use `-r` to ignore the checkpoint settings and re-run.

### About Crawling Result
There should be an `output.db` in your `save` directory once you execute with `-p` option. The scheme in sqlite3 db is defined as follows:
```yaml
messages:
  - name(unicode) // category name
  - id(int) // floor id / index id in each thread
  - thread_id(text) // the topic's thread id
  - message(text) // the message content for that index
```
You could use sqlite3 to access it:
```bash
bash$> sqlite3 output.db
SQLite version 3.16.0 2016-11-04 19:09:39
Enter ".help" for usage hints.
sqlite> select * from messages limit 2;
趣味一般|1|1112706898|トイレでするより､外で立ちションをするほうが､  解放感があって気持ちがいいですよね｡
趣味一般|2|1112706898|に（´・ω・２）
```
