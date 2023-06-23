from pathlib import Path
from unittest import TestCase

from aixm_geo.base import MultiPointAixm, SinglePointAixm
from aixm_geo.factory import AixmFeatureFactory
from aixm_geo.settings import NAMESPACES


class TestSinglePointAixm(TestCase):
    def setUp(self) -> None:
        file_loc = Path().absolute().joinpath('..', Path('test_data/donlon.xml'))
        ah_feature = AixmFeatureFactory(file_loc).root.xpath("/message:AIXMBasicMessage/message:hasMember/aixm"
                                                             ":AirportHeliport", namespaces=NAMESPACES)
        self.ah = SinglePointAixm(ah_feature[0])

    def test_get_first_value(self):
        name = self.ah.get_first_value('.//aixm:name')
        self.assertEqual('DONLON/DOWNTOWN HELIPORT', name)
        self.assertNotEqual('RANDOM AIRPORT NAME', name)
        self.assertTrue(isinstance(name, str))

    def test_get_first_value_attribute(self):
        attribute = self.ah.get_first_value_attribute('.//gml:endPosition', attribute_string='indeterminatePosition')
        self.assertEqual('unknown', attribute)
        self.assertNotEqual('Randomfdsajk;fdaskjhfdaskljh', attribute)

        attribute = self.ah.get_first_value_attribute('.//gml:endPosition')
        self.assertTrue(isinstance(attribute, dict))
        self.assertEqual('unknown', attribute['indeterminatePosition'])

    def test_get_elevation(self):
        elevation = self.ah.get_field_elevation()
        self.assertEqual(elevation, (0.0, 'M'))
        self.assertNotEqual(elevation, (0.0, 'FT'))
        self.assertTrue(isinstance(elevation, tuple))


class TestMultiPointAixm(TestCase):
    def setUp(self) -> None:
        file_loc = Path().absolute().joinpath('..', Path('test_data/donlon.xml'))
        airspace_feature = AixmFeatureFactory(file_loc).root.xpath("/message:AIXMBasicMessage/message:hasMember/"
                                                                   "aixm:Airspace", namespaces=NAMESPACES)
        self.airspace = MultiPointAixm(airspace_feature[0])
