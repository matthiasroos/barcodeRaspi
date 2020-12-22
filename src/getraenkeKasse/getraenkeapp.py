

from __future__ import annotations

import threading
from typing import Dict, List

import git
import wx

import functions
import getraenkeKasse
import src.app
import src.getraenkeKasse.adminframe
import src.getraenkeKasse.git
import src.getraenkeKasse.listframe
import src.getraenkeKasse.mainframe
import src.getraenkeKasse.scanframe
import src.getraenkeKasse.timer


class GetraenkeApp(src.app.App):
    """
    App ...
    """

    def __init__(self,
                 button_height: int,
                 button_width: int,
                 font_size: int,
                 offset: int,
                 file_names: Dict[str, str],
                 repositories: Dict[str, str]) -> None:
        super().__init__()

        self.display_settings.btn_height = button_height
        self.display_settings.btn_width = button_width
        self.display_settings.font_size = font_size
        self.display_settings.wx_button_size = wx.Size(self.display_settings.btn_width,
                                                       self.display_settings.btn_height)
        self.display_settings.wx_font = wx.Font(self.display_settings.font_size, wx.SWISS, wx.NORMAL, wx.BOLD)
        self.display_settings.off_set = offset

        self.products_file = file_names['products']
        self.purchases_file = file_names['purchases']
        self.users_file = file_names['users']

        self.repo_kasse = self.init_repo(path_repo=repositories['kasse'])
        self.repo_code = self.init_repo(path_repo=repositories['code'])

        self.version = getraenkeKasse.VERSION
        self.clicked_user = None

        # 30 minutes = 30 * 60 * 1000 milliseconds
        self.remote_update_timer = src.getraenkeKasse.timer.UpdateTimer(interval=30 * 60 * 1000,
                                                                        func=self.update_from_remote)

    def init_repo(self, path_repo: str) -> src.getraenkeKasse.git.GitRepository:
        """


        :param path_repo:
        :return:
        """
        try:
            repo = src.getraenkeKasse.git.GitRepository(path_repo=path_repo)
            return repo
        except git.InvalidGitRepositoryError as exc:
            self.show_error_dialog(error_message=f'Invalid Git Repository: {path_repo}')
            self.exit()

    def run(self) -> None:
        """
        Implementation of the abstract run method

        :return:
        """
        self.logger.info('starting up app')
        # check for new commits in local repository
        self.bring_git_repo_up_to_date(repo=self.repo_kasse,
                                       error_message='Problem with local git repo.',
                                       should_exit=True)
        # check for new version of getraenkeKasse.py script on github
        self.bring_git_repo_up_to_date(repo=self.repo_code,
                                       error_message='Problem with GitHub repository.',
                                       should_exit=True,
                                       restart_message='new version from gitHub, script is restarting...',
                                       should_restart=True)

        self.load_users()

        # # code for adding the paid column to PURCHASES_FILE
        # if functions.check_column_nr_in_file(self.purchases_file) == 3:
        #     functions.transform_purchases(purchases_file=self.purchases_file)
        #     functions.git_push(path_repo='./.',
        #                        files=[self.purchases_file],
        #                        commit_message='update PURCHASES_FILE via getraenkeKasse.py')
        self.load_purchases()
        #
        # # code for adding the stock column to PRODUCTS_FILE
        # if functions.check_column_nr_in_file(self.products_file) == 4:
        #     functions.transform_products(products_file=self.products_file)
        #     functions.git_push(path_repo='./.',
        #                        files=[self.products_file],
        #                        commit_message='update PRODUCTS_FILE via getraenkeKasse.py')
        self.load_products()

        src.getraenkeKasse.mainframe.MainFrame(self)
        self.remote_update_timer.Start(milliseconds=self.remote_update_timer.time_interval)
        self.app.MainLoop()

    def show_admin_frame(self) -> None:
        """
        Show the admin frame

        :return:
        """
        src.getraenkeKasse.adminframe.AdminFrame(self)

    def show_list_frame(self) -> None:
        """
        Show the list frame

        :return:
        """
        src.getraenkeKasse.listframe.ListFrame(self)

    def show_scan_frame(self) -> None:
        """
        Show the scan frame

        :return:
        """
        self.logger.info('scanframe shown')
        src.getraenkeKasse.scanframe.ScanFrame(self)

    def update_from_remote(self):
        """

        :return:
        """
        self.bring_git_repo_up_to_date(repo=self.repo_kasse)
        if self.repo_kasse.is_changed:
            self.logger.info('changes were fetched')
            self.load_products()
            self.load_purchases()
        else:
            self.logger.info('already up to date')

    def bring_git_repo_up_to_date(self,
                                  repo: src.getraenkeKasse.git.GitRepository,
                                  error_message: str = 'Problem with local git repo.',
                                  should_exit: bool = False,
                                  restart_message: str = '',
                                  should_restart: bool = False) -> None:
        """
        Pull all remote changes into the repository.

        :param repo:
        :param error_message: text of the error message in case of error
        :param should_exit: flag if function should exit in case of error
        :param restart_message: text of the info message in case of restart
        :param should_restart: flag if function should restart if changes were
        :return:
        """
        self.logger.info('starting git pull, repository path %s', repo.path_repo)
        self.queue.put(True)
        status = repo.pull()
        self.queue.get()
        if not status:
            self.show_error_dialog(
                error_message=f'{error_message}:\n{repo.error_message}\n{"Exiting now." if should_exit else ""}')
            if should_exit:
                self.exit()
        if repo.is_changed:
            if should_restart:
                self.show_info_dialog(info_message=restart_message)
                self.restart()
        self.logger.info('finished git pull, repository path %s', repo.path_repo)

    def _commit(self,
                repo: src.getraenkeKasse.git.GitRepository,
                files: List[str],
                commit_message: str,
                error_message: str = 'Problem with local git repo.') -> None:
        """
        Wrapper for repo.commit containing logging and an error dialog.

        :param repo:
        :param files: list of filenames to commit
        :param commit_message: commit message
        :param error_message: message in case of error
        :return:
        """
        self.logger.info('start')
        if not repo.commit(files=files, commit_message=commit_message):
            self.show_error_dialog(error_message=f'{error_message}\n{repo.error_message}')
        self.logger.info('finish')

    def _push(self,
              repo: src.getraenkeKasse.git.GitRepository,
              error_message: str = 'Problem with local git repo.') -> None:
        """
        Wrapper for repo.push with containing logging and an error dialog.

        :param repo:
        :param error_message: message in case of error
        :return:
        """
        self.logger.info('start')
        if not repo.push():
            self.show_error_dialog(error_message=f'{error_message}\n{repo.error_message}')
        self.logger.info('finish')

    def _set_stock_for_product(self,
                               nr: int,
                               stock: int) -> None:
        """
        Set the stock for a product to a new value.

        :param nr: number of the product
        :param stock: new stock for the product
        :return:
        """
        self.file_contents.products.loc[self.file_contents.products['nr'] == nr, 'stock'] = stock

    def _decrease_stock_for_product(self, code: str) -> bool:
        """
        Decrease the stock for a product by one.

        :param code: code of the product
        :return: True if there was stock to sell, False if not
        """
        if self.file_contents.products.loc[self.file_contents.products['code'] == code, 'stock'].values > 0:
            self.file_contents.products.loc[self.file_contents.products['code'] == code, 'stock'] -= 1
            return True
        return False

    def _set_paid_for_user(self, user: str) -> None:
        """
        Set all purchases for a user to True.

        :param user: paying user
        :return:
        """
        self.file_contents.purchases.loc[self.file_contents.purchases['user'] == user, 'paid'] = True

    @functions.runtime_profile(active=True)
    def save_admin_changes(self,
                           user_paid: List[str],
                           changed_stock: List[List[int, int, int]]) -> None:
        """


        :param user_paid: list of paying users
        :param changed_stock:
        :return:
        """
        def thread_function() -> None:
            self.queue.put(True)
            if user_paid:
                for user in user_paid:
                    self._set_paid_for_user(user=user)
                    self._save_purchases()
                    self._commit(repo=self.repo_kasse,
                                 files=[self.purchases_file],
                                 commit_message=f'pay for user {user} via getraenkeKasse.py')
            if changed_stock:
                for product in changed_stock:
                    nr, stock_old, stock_new = product
                    if stock_old != stock_new:
                        self._set_stock_for_product(nr=nr, stock=stock_new)
                self._save_products()
                self._commit(repo=self.repo_kasse,
                             files=[self.products_file],
                             commit_message='replenish stock via getraenkeKasse.py')
            self._push(repo=self.repo_kasse)
            self.queue.get()

        self.logger.info('start')
        thread = threading.Thread(target=thread_function)
        thread.start()
        self.logger.info('finish')

    @functions.runtime_profile(active=True)
    def make_purchase(self,
                      user: str,
                      code: str,
                      count: int) -> None:
        """
        Make purchases for user.

        :param user: buying user
        :param code: product code of bought item
        :param count: number of item to be bought
        :return:
        """
        def thread_function() -> None:
            self.queue.put(True)
            for _ in range(0, count):
                self.file_contents.purchases = functions.add_purchase(purchases=self.file_contents.purchases,
                                                                      user=user, code=code)
            self._save_purchases()
            files = [self.purchases_file]
            result_list = []
            for _ in range(0, count):
                result = self._decrease_stock_for_product(code=code)
                result_list.append(result)
            if any(result_list):
                self._save_products()
                files.append(self.products_file)
            if not any(result_list):
                # TODO issue warning for selling without stock
                pass
            self._commit(repo=self.repo_kasse,
                         files=files,
                         commit_message='purchase via getraenkeKasse.py')
            self._push(repo=self.repo_kasse)
            self.queue.get()
            return None

        self.logger.info('user %s, code %s, count %s', user, code, count)

        self.logger.info('start')
        thread = threading.Thread(target=thread_function)
        thread.start()
        self.logger.info('finish')

    @property
    def clicked_user(self) -> str:
        return self._clicked_user

    @clicked_user.setter
    def clicked_user(self, user: str) -> None:
        self._clicked_user = user
