from abc import abstractmethod, ABC

class TemplateNodePipeline(ABC):
    @abstractmethod
    def initiate(self):
        pass

    def start(self):
        pass

    @abstractmethod
    def update(self):
        pass

    def loop(self):
        pass

    @abstractmethod
    def stop(self):
        pass

