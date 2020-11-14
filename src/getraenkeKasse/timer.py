
import logging
from typing import Callable

import wx


class UpdateTimer(wx.Timer):
    """
    Timer class to call an update function in regular intervals
    """

    def __init__(self, interval: int, func: Callable, **kwargs) -> None:
        super().__init__()

        self.time_interval = interval
        self.func = func
        self.parameters = kwargs

        self.logger = logging.getLogger(self.__class__.__name__)

    def Notify(self) -> None:
        """
        Call the update function.

        :return:
        """
        self.logger.info(f'calling {self.func.__name__}()')
        self.func(**self.parameters)
