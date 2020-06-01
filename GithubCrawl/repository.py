import base64
import logging
import os

from github import GithubException

from metadata import Metadata


class Repository:

    def __init__(self, repository):
        self.repository = repository
        self.metadata = Metadata(
            html_url=repository.html_url,
            description=repository.description,
            stars=repository.stargazers_count,
            forks=repository.forks,
            watchers=repository.watchers
        )
        logging.basicConfig(level=logging.DEBUG)

    def save(self):
        """
        Compute the sha for the specified branch and save the contents
        and metadata to disk
        """
        branch_to_save = self.repository.default_branch
        sha = self.get_sha_for_branch(branch_to_save)
        base_path = os.path.join("code", self.repository.full_name)

        if not os.path.exists(base_path):
            os.makedirs(base_path)

        self.__save_contents(sha, "", base_path)
        self.metadata.save(os.path.join(os.path.join("code", self.repository.full_name), 'metadata.yml'))

    def __save_contents(self, sha, dir_content_path, base_path):
        """
        Save the contents recursively to disk.
        :param dir_content_path the path of the dir content found
        :param base_path the base path to store all the crawled code
        """
        contents = self.repository.get_dir_contents(dir_content_path, ref=sha)

        for content in contents:
            logging.debug("Processing %s", content.path)
            if content.type == 'dir':
                self.__save_contents(sha, content.path, base_path)
            elif content.name.endswith(".java"):
                if os.path.exists(os.path.join(base_path, content.path)):
                    continue
                try:
                    content = self.repository.get_contents(content.path, ref=sha)
                    data = base64.b64decode(content.content)
                    Repository.save_file(data, os.path.join(base_path, content.path))
                    self.metadata.files[content.path] = content.html_url
                except (GithubException, IOError) as exc:
                    logging.error('Error processing %s: %s', content.path, exc)

    def get_sha_for_branch(self, branch):
        """
        Return the last commit sha for the specified branch
        :param branch the branch to extract the last commit from
        :return the last commit sha used for decoding the contents
        """
        branches = self.repository.get_branches()
        matched_branches = [match for match in branches if match.name == branch]

        if not matched_branches:
            raise ValueError("Branch name not found")

        return matched_branches[0].commit.sha

    @staticmethod
    def save_file(data, path):
        """
        Save the file data to the specified path
        :param data: the data extracted from code files
        :param path: the path to disk to save the file
        """
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        file_out = open(path, "wb")
        file_out.write(data)
        file_out.close()
