import os
from operator import itemgetter

import elasticsearch
import flask
import logging
import yaml
from flask import request, jsonify, render_template

from index import Index
from query import Query

search_api = flask.Flask(__name__)
search_api.config["DEBUG"] = True
logging.basicConfig(level=logging.DEBUG)

index = Index('git_source', 'git_file')


class BadRequest(Exception):

    def __init__(self, message, status=400, payload=None):
        self.message = message
        self.status = status
        self.payload = payload


@search_api.errorhandler(BadRequest)
def handle_bad_request(error):
    """
    Handles bad request error
    :param error: the bad request error
    :return: the json response payload and the status code of the error
    """
    payload = {
        'status': error.status,
        'message': error.message
    }

    return jsonify(payload), 400


@search_api.errorhandler(elasticsearch.exceptions.NotFoundError)
def handle_index_not_found(error):
    """
    Handles the index not found exception
    :param error: the not found error
    :return: the json response payload and the status code of the error
    """
    payload = {
        'status': error.status_code,
        'message': error.info
    }

    return jsonify(payload), error.status_code


@search_api.route('/frontend', methods=['GET'])
def frontend():
    """
    Exposes the endpoint used from the frontend
    :return:
    """
    return render_template('frontend.html')


@search_api.route('/search', methods=['POST'])
def search():
    """
    Exposes the search endpoint
    :return: the response in json format
    """
    content = request.json

    if not content:
        raise BadRequest("Content json can't be empty")

    query = Query(content['query'], parse_filters(content))

    search_result = index.search("git_source", query.create())

    response = _create_json_response(content['checked'], search_result)

    return jsonify(response)


def _create_json_response(sort, search_result):
    """
    Creates the json with the needed information extracted from complex
    elasticsearch response
    :param sort: defines how to sort the results
    :param search_result: the results from elasticsearch
    :return: the json response
    """
    time = search_result['took']
    hits = search_result['hits']['hits']
    response_hits = []

    for hit in hits:
        content = hit['_source']['function']['content']
        name = hit['_source']['function']['name']
        repo_name = hit['_source']['repo_name']
        url = hit['_source']['url']
        forks = hit['_source']['function']['forks']
        stars = hit['_source']['function']['stars']
        watchers = hit['_source']['function']['watchers']
        score = hit['_score']

        response_hit = {
            "name": name,
            "content": content,
            "repo_name": repo_name,
            "url": url,
            "forks": forks,
            "stars": stars,
            "watchers": watchers,
            "score": score
        }

        response_hits.append(response_hit)

    response_hits = sorted(
        response_hits,
        key=itemgetter(sort),
        reverse=True
    )

    return {
        "time": time,
        "hits": response_hits
    }


def parse_filters(content):
    """
    Parses the filters the user gave
    :param content: the json content of the request
    :return: filters the extracted filters the user send
    """
    available_filters = [
        "returnType",
        "methodName",
        "modifiers",
        "variables",
    ]

    filters = {}
    for content_key in content.keys():

        # query attribute is not considered filter
        if content_key == "query" or content_key == 'checked':
            continue

        if content_key not in available_filters:
            raise BadRequest("Unknown filter " + str(content_key))

        filters[content_key] = content[content_key]

    return filters


def main():
    config_path = "config/config.yml"
    if os.path.exists(config_path):
        with open(config_path, 'rt') as f:
            config_file = yaml.safe_load(f.read())
            search_api.run(**config_file['api'])
    else:
        search_api.run(port=8080)


if __name__ == "__main__":
    main()
