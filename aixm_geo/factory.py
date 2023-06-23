from lxml import etree

import aixm_features as af
import util as util
from settings import NAMESPACES


class AixmFeatureFactory:
    __slots__ = ["_root", '_feature_classes', '_errors']

    def __init__(self, root):
        self.root = root
        self._feature_classes = {
            'AirportHeliport': af.AirportHeliport,
            'DesignatedPoint': af.DesignatedPoint,
            'NavaidComponent': af.NavaidComponent,
            'RouteSegment': af.RouteSegment,
            'Airspace': af.Airspace,
            'VerticalStructure': af.VerticalStructure,
        }
        self._errors = []

    def __iter__(self):
        return self.get_feature_details()

    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, root):
        self._root = etree.parse(root)

    @property
    def errors(self):
        return self._errors

    @errors.setter
    def errors(self, value):
        self._errors.append(value)

    def get_feature_details(self):
        """
        Iterates through the root of the AIXM file and returns a generator of AIXMFeature objects
        Returns:

        """
        aixm_features = self._root.iterfind('.//message:hasMember', NAMESPACES)
        for feature in aixm_features:
            aixm_feature = self.produce(feature)
            if aixm_feature:
                yield aixm_feature
            else:
                pass

    def produce(self, subroot):
        """
        Produces an individual AIXMFeature object from the subroot
        Args:
            subroot:

        Returns:

        """
        feature_type = util.get_feature_type(subroot)
        try:
            aixm_feature = self._feature_classes[feature_type](subroot)
        except KeyError:
            self.errors = f'aixm:{feature_type} is not a currently supported AIXMFeature type'
            aixm_feature = None
        finally:
            return aixm_feature
