from abc import abstractmethod, ABC
from constants.constants_enum import StageStatus
import logging

class TemplateNodeStage(ABC):
    def __init__(self):
        self.status_handlers = {
            StageStatus.Wait: self.wait,
            StageStatus.Execute: self.execute,
            StageStatus.Stop: self.stop,
            StageStatus.Error: self.error
        }

    @abstractmethod
    def wait(self) -> None:
        pass

    @abstractmethod
    def execute(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def error(self) -> None:
        pass

    @abstractmethod
    def loof(self) -> None:
        pass
