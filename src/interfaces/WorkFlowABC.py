from abc import ABC,abstractmethod
from typing import Any
class IWorkFlow(ABC):
    # 工作流的接口
    @abstractmethod
    def create_node(self, *args, **kwargs) -> Any:
        """
        创建节点
        """
        pass
    @abstractmethod
    def create_edge(self, *args, **kwargs) -> Any:
        """
        建边
        """
        pass

    @abstractmethod
    def create_graph(self, *args, **kwargs) -> Any:
        """
        建工作流
        """
        pass






