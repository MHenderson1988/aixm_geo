from abc import ABC, abstractmethod


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
