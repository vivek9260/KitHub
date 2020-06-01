#GitHub Search
## Project Members: 
   - Jade Cock
   - Vivek Chalumuri
   - Stavros Giorgis
   - Romina Arriaza Barriga 

## System requirements
   - Python 3.6 or later
   - requests 2.13.0 or later
   - Flask 0.12.2
   - elasticsearch 7.0.1
   - nltk 3.2.5
   - javalang 0.11.0
   - beautifulsoup4 4.7.1
   - PyGithub 1.43.7
   - PyYAML 5.1

```
pip install -r requirements.txt
```

## Crawling
```
cd GithubCrawl/
mkdir -p code

python crawl.py --username=user --password=pass --query="query language:java"
```

## Processing
Replace the tokenize.py file inside the javalang package with the our tokenizer.py file

```
python process_files.py --code=<path_to_code_folder>
```

## Indexing

First you should start elastic search server.
After you start the server you should delelte any previously create git_source index
```
CURL -XDELETE localhost:9200/git_source
```

The search engine API will index our records once is started.
## Starting the Search Engine
```
cd GihubSearchEngine/
```

Edit the config file found in config/config.yml to add the path to the records json created by the Processing part
You can also define host and port for ElasticSearch, as well as the port for the api.

```
python search_api.py
```

## Using UI

Connect to http://localhost:8080/frontend?#! in your browser




