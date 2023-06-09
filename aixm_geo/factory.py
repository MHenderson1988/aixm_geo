from lxml import etree

import aixm_geo.aixm_features as af
import aixm_geo.util as util
from aixm_geo.settings import NAMESPACES


class AixmFeatureFactory:
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
        aixm_features = self._root.findall('.//message:hasMember', NAMESPACES)
        aixm_feature_list = []
        for feature in aixm_features:
            feature = self.produce(feature)
            if feature:
                aixm_feature_list.append(feature)
            else:
                pass
        return aixm_feature_list

    def produce(self, subroot):
        timeslice = util.parse_timeslice(subroot)
        feature_type = util.get_feature_type(subroot)
        try:
            aixm_feature = self._feature_classes[feature_type](subroot, timeslice)
        except KeyError:
            self.errors = f'aixm:{feature_type} is not a currently supported AIXMFeature type'
            aixm_feature = None
        finally:
            return aixm_feature


