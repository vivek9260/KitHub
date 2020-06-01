import json
import os

from elasticsearch import Elasticsearch
import logging
import yaml


class Index:

    def __init__(self, name, doc_type):
        self.name = name
        self.doc_type = doc_type
        self.elasticsearch = None
        self.create_elasticsearch()
        self.create_index()

    def search(self, index_name, search):
        """
        :param index_name: String indicating the name of the index
        we want to look in
        :param search: search query
        :return:
        res: result of the search
        """
        return self.elasticsearch.search(
            index=index_name,
            body=search
        )

    def create_elasticsearch(self):
        """
        Creates the elasticsearch instance based on the elasticsearch.yml file.
        """

        config_path = "config/config.yml"
        if os.path.exists(config_path):
            with open(config_path, 'rt') as f:
                config_file = yaml.safe_load(f.read())
                self.elasticsearch = Elasticsearch([config_file['elasticsearch']])
        else:
            self.elasticsearch = Elasticsearch([{'host': 'localhost', 'port': 9200}])

    def create_index(self):
        """
        Function in charge of creating the index establishing the mapping of
        each object (structure attributes)
        """

        if self.elasticsearch.indices.exists(self.name):
            return

        try:
            self.elasticsearch.indices.create(
                index=self.name
            )
            self.store_records()
        except Exception as ex:
            logging.error(str(ex))

    def store_record(self, record):
        """
        Function in charge of storing the record into the index
        :param record: json object to store
        """
        try:
            self.elasticsearch.index(
                index=self.name,
                doc_type=self.doc_type,
                body=record
            )
        except Exception as ex:
            logging.error(str(ex))

    def store_records(self):
        """
        Store all records extracted from the records json file
        """
        config_path = "config/config.yml"
        if os.path.exists(config_path):
            with open(config_path, 'rt') as f:
                    config_file = yaml.safe_load(f.read())
            with open(config_file['elasticsearch']['records']) as yml_file:
                data = json.load(yml_file)

            for data_entry in data.values():
                self.store_record(Index.create_record(**data_entry))

    @staticmethod
    def create_record(name, class_name, repo_name,
                      modifiers, content,
                      github_url, return_type,
                      start_line, end_line, variables,
                      forks, stars, watchers, javadoc):
        """
        Creates the record json file based on the attributes extracted from the records json file
        :return: record_json to
        """
        function_json = {
            "name": name,
            "modifiers": modifiers,
            "variables": variables,
            "return_type": return_type,
            "start_line": start_line,
            "end_line": end_line,
            "class_name": class_name,
            "content": content,
            "forks": forks,
            "stars": stars,
            "watchers": watchers,
            "javadoc": javadoc
        }

        record_json = {
            "repo_name": repo_name,
            "url": github_url,
            "function": function_json
        }

        return record_json
