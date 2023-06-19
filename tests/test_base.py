from pathlib import Path
from unittest import TestCase
from aixm_geo.base import MultiPointAixm, SinglePointAixm
from aixm_geo.factory import AixmFeatureFactory
from aixm_geo.settings import NAMESPACES


class TestSinglePointAixm(TestCase):
    def setUp(self) -> None:
        file_loc = Path().absolute().joinpath('..', Path('test_data/test.xml'))
        features = AixmFeatureFactory(file_loc).root.findall('.//message:hasMember', NAMESPACES)
        self.ah = SinglePointAixm(features[0])

    def test_get_first_value(self):
        name = self.ah.get_first_value('.//aixm:name')
        self.assertEqual('SAINT ETIENNE MALACUSSY', name)
        self.assertNotEqual('RANDOM AIRPORT NAME', name)
        self.assertTrue(isinstance(name, str))

    def test_get_first_value_attribute(self):
        attribute = self.ah.get_first_value_attribute('.//gml:endPosition', attribute_string='indeterminatePosition')
        self.assertEqual('unknown', attribute)
        self.assertNotEqual('Randomfdsajk;fdaskjhfdaskljh', attribute)

        attribute = self.ah.get_first_value_attribute('.//gml:endPosition')
        self.assertTrue(isinstance(attribute, dict))
        self.assertEqual('unknown', attribute['indeterminatePosition'])


class TestMultiPointAixm(TestCase):
    def setUp(self) -> None:
        file_loc = Path().absolute().joinpath('..', Path('test_data/test_airspace.xml'))
        features = AixmFeatureFactory(file_loc).root.findall('.//message:hasMember', NAMESPACES)
        self.airspace = MultiPointAixm(features[0])

    def test_get_coordinate_list(self):
        subroot = self.airspace._root.findall('.//aixm:theAirspaceVolume//aixm:horizontalProjection//gml:segments',
                                     namespaces=NAMESPACES)
        coordinate_list = self.airspace.get_coordinate_list(subroot)
        self.assertTrue(isinstance(coordinate_list, list))
        for string in coordinate_list:
            self.assertTrue(isinstance(string, str))

