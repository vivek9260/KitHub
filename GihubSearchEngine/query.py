class Query:
    def __init__(self, query, filters, size=100):
        self.query = query
        self.size = size
        self.filters = filters
        self.mappings = {
            "methodName": "function.name",
            "returnType": "function.return_type",
            "modifiers": "function.modifiers",
            "variables": "function.variables"
        }

    def create(self):
        """
        Creates the query json format for the elastic search
        :return: the json representation of the query object
        """
        matches = self.apply_filters()
        matches.append(self.create_query())

        query = {
            "size": self.size,
            "query": {
                "bool": {
                    "must": matches
                }
            }
        }

        return query

    def boost_term_query(self):
        """
        Boost the query terms for a two term query and make wildcard any one term query
        :return:
        """
        if len(self.query.split()) == 2:
            self.query = self.query.replace(" ", "") + "^10.0" + " " + self.query
        elif len(self.query.split()) == 1:
            self.query = "*" + self.query + "*"

    def create_query(self):
        """
        Creates the query in json format for elasticsearch using the query and the filters
        :return: the query in json format
        """

        self.boost_term_query()

        return {
            "bool": {
                "should": [
                    {
                        "query_string": {
                            "fields": [
                                "function.name"
                            ],
                            "query": self.query,
                            "boost": 5
                        }
                    },
                    {
                        "query_string": {
                            "fields": [
                                "function.class_name"
                            ],
                            "query": self.query,
                            "boost": 4
                        }
                    },
                    {
                        "query_string": {
                            "fields": [
                                "function.content"
                            ],
                            "query": self.query,
                            "boost": 3
                        }
                    },
                    {
                        "query_string": {
                            "fields": [
                                "function.javadoc"
                            ],
                            "query": self.query,
                            "boost": 2
                        }
                    },
                    {
                        "query_string": {
                            "fields": [
                                "function.variables",
                                "function.modifiers",
                                "function.return_type",
                                "repo_name",
                                "url"
                            ],
                            "query": self.query
                        }
                    }
                ]
            }
        }

    def apply_filters(self):
        """
        Apply the filters the user provided and generate the json format of the filters in the query
        :return: the json format of the filters part in the query
        """
        filters = []
        for filter_key in self.filters.keys():
            if self.filters[filter_key]:
                filters.append(dict(
                    query_string={
                        "fields": [self.mappings[filter_key]],
                        "query": self.filters[filter_key]
                    }
                ))
        return filters
