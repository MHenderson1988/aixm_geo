from pathlib import Path
from unittest import TestCase
from aixm_geo.base import MultiPointAixm, SinglePointAixm
from aixm_geo.factory import AixmFeatureFactory
from aixm_geo.aixm_geo import AixmGeo


class TestBase(TestCase):
    def setUp(self):
        file_loc = Path().absolute().joinpath('..', Path('test_data/test.xml'))
        self.test_obj = SinglePointAixm(AixmGeo(file_loc), )

    def test_get_feature_type(self):
        # Test for AirportHeliport
        self.assertEqual(self.ah.feature_type, 'AirportHeliport')

    def test_parse_timeslice(self):
        self.assertEqual(len(self.ah.parse_timeslice()), 1)
        self.assertTrue(isinstance(self.ah.parse_timeslice(), list))

    def test_get_first_value(self):
        self.assertEqual('FAIR ISLE', self.ah.get_first_value('.//aixm:name'))
        self.assertEqual('237.05', self.ah.get_first_value('.//aixm:fieldElevation'))
        self.assertEqual('161', self.ah.get_first_value('.//aixm:ARP//aixm:geoidUndulation'))

    def test_get_first_value_attribute(self):
        self.assertEqual('FT', self.ah.get_first_value_attribute('.//aixm:fieldElevation', attribute_string='uom'))
        self.assertTrue(isinstance(self.ah.get_first_value_attribute('.//aixm:fieldElevation'), dict))

    def test_determine_arc_direction(self):
        self.assertEqual('clockwise', self.airspace.determine_arc_direction(25, 200))
        self.assertEqual('anticlockwise', self.airspace.determine_arc_direction(250, 200))
        self.assertNotEqual('clockwise', self.airspace.determine_arc_direction(250, 200))
        self.assertNotEqual('anticlockwise', self.airspace.determine_arc_direction(25, 200))