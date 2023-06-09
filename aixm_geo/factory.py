from lxml import etree

import aixm_geo.aixm_features as af
import aixm_geo.util as util
from aixm_geo.settings import NAMESPACES


class AixmFeatureFactory:
    def __init__(self, root):
        self._root = root
        self._feature_classes = {
            'AirportHeliport': af.AirportHeliport,
            'DesignatedPoint': af.DesignatedPoint,
            'NavaidComponent': af.NavaidComponent,
            'RouteSegment': af.RouteSegment,
            'Airspace': af.Airspace
        }

    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, root):
        if isinstance(root, etree._Element):
            self._root = root
        else:
            raise TypeError(f'Root can only accept type lxml etree.Element')

    def get_feature_details(self):
        aixm_features = self._root.findall('.//message:hasMember', NAMESPACES)
        for feature in aixm_features:
            self.produce(feature)

    def produce(self, subroot):
        timeslice = util.parse_timeslice()
        feature_type = util.get_feature_type(subroot)
        try:
            aixm_feature = self._feature_classes[feature_type](subroot, timeslice). \
                get_geographic_information()
        except KeyError:
            print(f'aixm:{feature_type} is not a currently supported AIXMFeature type')
            aixm_feature = None
        return aixm_feature
