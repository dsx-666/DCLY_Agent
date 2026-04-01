from abc import ABC,abstractmethod
from typing import Any
class IToolNode(ABC):
    # 工具的接口
    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        """
        :param 传入的参数
        :return 返回的结果
        """
        pass

    @abstractmethod
    def __call__(self, *args, **kwargs) -> Any:
        """
        :param 传入的参数
        :return 返回的结果
        """
        pass

