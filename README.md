# GitHub Search

This project is part of the course DD2476, Search Engines and Information Retrieval Systems.

## Abstract 

Reusing existing code can prove to be a precious gain of time. In this project, a subset of all the java repositories publicly available on Github has been crawled, processed and indexed into elastic search. The aim is to build a platform where a user can retrieve their function of interest if it has already been implemented. We evaluate this platform by computing the normalised discounted cumulative gain (nDCG) over three queries of various difficulties and test the user friendliness of the user interface. It is found that enabling the boosting functionality function improves the nDCG in most cases and that the engine is able to retrieve the functions
of interest in the top results.

## Project Members: 
   - Jade Cock
   - Stavros Giorgis
   - Vivek Chalumuri
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




