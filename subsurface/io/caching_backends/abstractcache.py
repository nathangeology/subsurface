from abc import ABC, abstractmethod


class AbstractCache(ABC):

    @abstractmethod
    def write_to_cache(self, name, data_structure):
        pass

    @abstractmethod
    def read_from_cache(self, name):
        pass

    @abstractmethod
    def check_cache(self, name):
        pass

    @abstractmethod
    def delete_from_cache(self, name):
        pass
