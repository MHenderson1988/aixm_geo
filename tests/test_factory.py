from pathlib import Path
from unittest import TestCase
from lxml import etree
from aixm_geo.factory import AixmFeatureFactory
from aixm_geo.interfaces import IAixmFeature
from aixm_geo.settings import NAMESPACES


class TestAixmFeatureFactory(TestCase):
    def setUp(self) -> None:
        file_loc = Path().absolute().joinpath('..', Path('test_data/test.xml'))
        self.test_factory = AixmFeatureFactory(file_loc)

    def test_root(self):
        # Try invalid input, should throw an OS error
        with self.assertRaises(OSError):
            self.test_factory.root = 'Hello'

        # Test it is an ElementTree
        self.assertTrue(isinstance(self.test_factory.root, etree._ElementTree))

    def test_get_feature_details(self):
        feature_list = self.test_factory.get_feature_details()
        self.assertTrue(isinstance(feature_list, list))
        for feature in feature_list:
            self.assertTrue(isinstance(feature, IAixmFeature))

    def test_produce(self):
        feature_list = self.test_factory.root.findall('.//message:hasMember', NAMESPACES)
        valid_feature = self.test_factory.produce(feature_list[0])  # This is an AirportHeliport
        self.assertTrue(isinstance(valid_feature, IAixmFeature))

        invalid_feature = self.test_factory.produce(feature_list[2000])  # Pick a currently unsupport feature type.
        self.assertFalse(invalid_feature)
