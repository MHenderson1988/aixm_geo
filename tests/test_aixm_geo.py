from pathlib import Path
from unittest import TestCase

from lxml import etree

from aixm_geo.aixm_geo import AixmGeo


class TestAixmGeo(TestCase):
    def setUp(self):
        file_loc = Path().absolute().joinpath('..', Path('test_data/test.xml'))
        self.test_aixm = AixmGeo(file_loc)

    def test_extract_geo_info(self):
        test_info = self.test_aixm.extract_geo_info()
        self.assertTrue(isinstance(test_info, list))
