from abc import ABC, abstractmethod


class IAixmGeo(ABC):
    @property
    @abstractmethod
    def root(self):
        pass

    @abstractmethod
    def extract_geo_info(self):
        pass


class IGeoExtractor(ABC):
    @property
    @abstractmethod
    def root(self):
        pass

    @property
    @abstractmethod
    def feature_type(self):
        pass

    @property
    @abstractmethod
    def timeslices(self):
        pass
