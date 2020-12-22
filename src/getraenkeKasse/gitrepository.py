
from __future__ import annotations

import datetime
import os
from typing import Optional

import git

import functions


class GitRepository:
    """
    High-level representation of a git repository based on gitPython.
    """
    def __init__(self, path_repo: str) -> None:
        self.path_repo: str = path_repo

        self.repo = git.Repo(self.path_repo)

        self.is_changed: bool = None # noqa
        self.error_message: Optional[str] = None

    @functions.check_environment_TEST_PROD
    def pull(self) -> bool:
        """
        Execute "git pull" on a repository.

        :return: error status of the executed command, True: success, False: failure
        """
        try:
            current = self.repo.head.commit
            self.repo.remotes.origin.pull()
            if current != self.repo.head.commit:
                self.is_changed = True
            else:
                self.is_changed = False
            self.error_message = None
            return True
        except git.GitError as exc:
            self.error_message = f'{exc}'
            return False

    @functions.check_environment_TEST_PROD
    def fetch_rebase(self) -> bool:
        """


        :return: error status of the executed command, True: success, False: failure
        """
        pass

    @functions.check_environment_TEST_PROD
    def commit(self, files: list[str], commit_message: str) -> bool:
        """
        Add and commit files to the repository.

        :param files: files to be committed
        :param commit_message: message for the commit
        :return: error status of the executed command, True: success, False: failure
        """
        self.error_message = None
        try:
            if files:
                self.repo.index.add(items=files)
                self.repo.index.commit(message=commit_message)
                return True
            return False
        except git.GitError as exc:
            self.error_message = f'{exc}'
            return False

    @functions.check_environment_TEST_PROD
    def push(self) -> bool:
        """


        :return: error status of the executed command, True: success, False: failure
        """
        try:
            # TODO: check if it is necessary to push
            self.repo.remotes.origin.push()
            return True
        except git.GitError as exc:
            self.error_message = f'{exc}'
            return False

    @property
    def last_fetch(self) -> Optional[datetime.datetime]:
        """


        :return:
        """
        try:
            m_time = os.path.getmtime(f'{self.path_repo}/.git/FETCH_HEAD')
            return datetime.datetime.fromtimestamp(m_time)
        except FileNotFoundError:
            return None
