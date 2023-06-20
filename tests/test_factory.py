from pathlib import Path
from unittest import TestCase
from lxml import etree
from aixm_geo.factory import AixmFeatureFactory


class TestAixmFeatureFactory(TestCase):
    def setUp(self) -> None:
        file_loc = Path().absolute().joinpath('..', Path('test_data/donlon.xml'))
        self.test_factory = AixmFeatureFactory(file_loc)

    def test_root(self):
        # Try invalid input, should throw an OS error
        with self.assertRaises(OSError):
            self.test_factory.root = 'Hello'

        # Test it is an ElementTree
        self.assertTrue(isinstance(self.test_factory.root, etree._ElementTree))
