import logging
import os
import argparse
import yaml

from github import Github
from repository import Repository

parser = argparse.ArgumentParser()
parser.add_argument('--username', type=str, dest="username")
parser.add_argument('--password', type=str, dest="password")
parser.add_argument('--query', type=str, dest="query")

args = parser.parse_args()

username = args.username
password = args.password

query = args.query

github = Github(username, password)

repositories_config_path = "code/repositories.yml"
if os.path.exists(repositories_config_path):
    with open(repositories_config_path, 'rt') as f:
        saved_repositories = yaml.safe_load(f.read())
else:
    saved_repositories = {}

repositories = github.search_repositories(query=query)

# store the current repository in case exception in API before saving
current_repository = None

try:
    for repository in repositories:
        if repository.full_name not in saved_repositories.keys():
            repository = Repository(repository)
            current_repository = repository
            repository.save()
            saved_repositories[repository.repository.full_name] = repository.repository.url

except Exception as ex:
    logging.error(msg=ex)
finally:
    if current_repository.repository.full_name not in saved_repositories.keys():
        current_repository.metadata.save(
            os.path.join(os.path.join("code", current_repository.repository.full_name), 'metadata.yml')
        )
        saved_repositories[current_repository.repository.full_name] = current_repository.repository.url

    with open(repositories_config_path, 'w') as outfile:
        yaml.dump(saved_repositories, outfile, default_flow_style=False)
