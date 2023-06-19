from lxml import etree

import aixm_geo.aixm_features as af
import aixm_geo.util as util
from aixm_geo.settings import NAMESPACES


class AixmFeatureFactory:
    __slots__ = ["_root", '_feature_classes', '_errors']

    def __init__(self, root):
        self.root = root
        self._feature_classes = {
            'AirportHeliport': af.AirportHeliport,
            'DesignatedPoint': af.DesignatedPoint,
            'NavaidComponent': af.NavaidComponent,
            'RouteSegment': af.RouteSegment,
            'Airspace': af.Airspace
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
        aixm_features = self._root.iterfind('.//message:hasMember', NAMESPACES)
        for feature in aixm_features:
            aixm_feature = self.produce(feature)
            if aixm_feature:
                yield aixm_feature
            else:
                pass

    def produce(self, subroot):
        feature_type = util.get_feature_type(subroot)
        try:
            aixm_feature = self._feature_classes[feature_type](subroot)
        except KeyError:
            self.errors = f'aixm:{feature_type} is not a currently supported AIXMFeature type'
            aixm_feature = None
        finally:
            return aixm_feature
