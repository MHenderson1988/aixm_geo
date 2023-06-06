from pathlib import Path
from unittest import TestCase

from lxml import etree

from aixm_geo.aixm_geo import AixmGeo, GeoExtractor


class TestAixm(TestCase):
    def setUp(self):
        file_loc = Path().absolute().joinpath('..', Path('test_data/test.xml'))
        self.test_aixm = AixmGeo(file_loc)

    def test_find_aixm_features(self):
        list_of_features = self.test_aixm.find_aixm_features()
        self.assertTrue(isinstance(list_of_features, list))
        for i in list_of_features:
            self.assertTrue(isinstance(i, etree._Element))


class TestGeoExtractor(TestCase):
    def setUp(self):
        file_loc = Path().absolute().joinpath('..', Path('test_data/test.xml'))
        self.a = AixmGeo(file_loc)
        # AirportHeliport
        self.ah = GeoExtractor(self.a.find_aixm_features()[0])
        # Navaid
        self.na = GeoExtractor(self.a.find_aixm_features()[1])
        # Airspace with Arc
        self.airspace = GeoExtractor(self.a.find_aixm_features()[2])
        # Airspace with Circle
        self.airspace_circle = GeoExtractor(self.a.find_aixm_features()[3])
        # RouteSegment
        self.route_segment = GeoExtractor(self.a.find_aixm_features()[5])

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

    def test_get_arp_coordinates(self):
        self.assertEqual('59.5347278 -1.6285111 237.05 FT', f'{self.ah.properties["coordinates"]}'
                                                            f' {self.ah.properties["elevation"]}'
                                                            f' {self.ah.properties["elevation_uom"]}')

    def test_get_navaid_coordinates(self):
        self.assertEqual('53.2814667 -0.9471639 115 FT', f'{self.na.properties["coordinates"]}'
                                                         f' {self.na.properties["elevation"]}'
                                                         f' {self.na.properties["elevation_uom"]}')

    def test_get_route_segment_coordinates(self):
        self.assertEqual('51.540220667 0.977041556, 51.531229778 0.388494583',
                         self.route_segment.properties["coordinates"])

    def test_determine_arc_direction(self):
        self.assertEqual('clockwise', self.airspace.determine_arc_direction(25, 200))
        self.assertEqual('anticlockwise', self.airspace.determine_arc_direction(250, 200))
        self.assertNotEqual('clockwise', self.airspace.determine_arc_direction(250, 200))
        self.assertNotEqual('anticlockwise', self.airspace.determine_arc_direction(25, 200))
