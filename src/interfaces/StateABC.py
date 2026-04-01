from abc import ABC,abstractmethod
from typing import Any

from pydantic import BaseModel

class IState(BaseModel,ABC):
    """ pydantic字段 """
    input_config:dict



class IStateMachine(ABC):
    # 状态的实现的接口
    @abstractmethod
    def create_state(self, *args, **kwargs) -> Any:
        """
        创建状态
        :param 传入的参数
        :return BaseModel 状态
        """
        pass