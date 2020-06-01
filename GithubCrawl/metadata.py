import yaml


class Metadata:
    def __init__(self, html_url, description, stars, forks, watchers):
        self.html_url = html_url
        self.description = description
        self.stars = stars
        self.forks = forks
        self.watchers = watchers
        self.files = {}

    def save(self, path):
        """
        Save the metadata for a repository on the dist
        """
        data = dict(
            html_url=self.html_url,
            description=self.description,
            stars=self.stars,
            forks=self.forks,
            watchers=self.watchers,
            files=self.files
        )
        with open(path, 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)
