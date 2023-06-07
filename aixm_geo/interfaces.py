from abc import ABC, abstractmethod


class IAixmFeatureGeoExtractor(ABC):
    @property
    @abstractmethod
    def root(self):
        pass

    @property
    @abstractmethod
    def timeslices(self):
        pass

    @abstractmethod
    def get_first_value(self, xpath):
        pass

    @abstractmethod
    def get_all_values(self, xpath):
        pass

    @abstractmethod
    def get_first_value_attribute(self, xpath):
        pass


class IAixmFeature(ABC):
    """
    Interface used for AIXM features who's geographic information typically consists of a single point

    *AirportHeliport
    *DesignatedPoint
    *Navaid etc.
    """

    @abstractmethod
    def get_geographic_information(self) -> dict:
        pass
