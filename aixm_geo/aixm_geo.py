from datetime import datetime
from pathlib import Path
from typing import Union

from lxml import etree
from pyproj.geod import Geod


class AixmGeo:
    def __init__(self, root: Union[str, Path]):
        self.root = etree.parse(root)
        self.namespaces = {'xlink': "http://www.w3.org/1999/xlink",
                           'gml': "http://www.opengis.net/gml/3.2", 'aixm': "http://www.aixm.aero/schema/5.1",
                           'nats': "http://www.aixm.aero/schema/5.1/extensions/NATS/eSDO",
                           'message': "http://www.aixm.aero/schema/5.1/message",
                           'xsi': "http://www.w3.org/2001/XMLSchema-instance"}

    def find_aixm_features(self) -> list:
        feature_list = self.root.findall('.//message:hasMember', self.namespaces)
        return feature_list

    def extract_geo_info(self) -> list:
        feature_list = self.find_aixm_features()
        geo_info = [GeoExtractor(x).get_geo_info() for x in feature_list]
        for x in geo_info:
            print(x)
        return geo_info


class GeoExtractor:
    def __init__(self, root: etree.Element):
        self.root = root
        self.namespaces = {'xlink': "http://www.w3.org/1999/xlink",
                           'gml': "http://www.opengis.net/gml/3.2", 'aixm': "http://www.aixm.aero/schema/5.1",
                           'nats': "http://www.aixm.aero/schema/5.1/extensions/NATS/eSDO",
                           'message': "http://www.aixm.aero/schema/5.1/message",
                           'xsi': "http://www.w3.org/2001/XMLSchema-instance"}
        self.timeslices = self.parse_timeslice()
        self.feature_type = self.get_feature_type()

    def get_feature_type(self) -> str:
        try:
            feature_type = self.timeslices[-1].find('.//', self.namespaces).tag.split('}')[-1].split('T')[0]

        except IndexError:
            feature_type = "Unknown"
        return feature_type

    def parse_timeslice(self) -> list:
        """Looks at the timeslices contained within the feature and arranges them in time order (oldest to newest).

        Returns:
            timeslices (list):
                A list of timeslices in chronological order.

        """
        # Get a list of timeslices
        try:
            timeslices = self.root.findall('.//aixm:timeSlice', self.namespaces)
        except IndexError:
            timeslices = None
        # Don't bother to sort if there is only one timeslice
        if len(timeslices) > 1:
            timeslices.sort(key=lambda x: datetime.strptime(
                x.find('.//{http://www.aixm.aero/schema/5.1}versionBegin').text.split('T')[0],
                "%Y-%m-%d"))
        return timeslices

    def get_first_value(self, xpath: str, **kwargs: etree.Element) -> str:
        """Returns the first matching text value found within the subtree which match the Xpath provided.

        Args:
            xpath (str): Valid Xpath string for the value to try and find.
            **kwargs:
                subtree(etree.Element): The subtree to search.  Defaults to self.root if no value provided.
        Returns:
            value (str): String value of the tag found.
        """
        subtree = kwargs.pop('subtree', self.root)
        try:
            value = subtree.find(xpath, namespaces=self.namespaces).text
            if value is None:
                raise AttributeError
        except AttributeError:
            value = "Unknown"
        return value

    # XPath with namespace example = self.root.xpath('//aixm:name', namespaces=self.namespace)
    # Uses findall as opposed to find
    def get_all_values(self, xpath: str, **kwargs: etree.Element):
        """Returns a list of all values within the subtree which match the Xpath provided
        Args:
            xpath (str): Valid Xpath string for the tag to try and find.
            **kwargs:
                subtree(etree.Element): The subtree to search.  Defaults to self.root if no value provided.
        Returns:
            values(list): List of string values found.
        """
        subtree = kwargs.pop('subtree', self.root)
        try:
            values = subtree.findall(xpath, namespaces=self.namespaces)
            if values is None:
                raise AttributeError
            else:
                values = [x.text for x in values]
        except AttributeError:
            values = "Unknown"
        return values

    def get_first_value_attribute(self, xpath: str, **kwargs: Union[etree.Element, str]) -> Union[str, dict]:
        """
        Args:
            xpath (str): Valid Xpath string for the tag to try and find.
            **kwargs:
                subtree (etree.Element):  The subtree to search.  Defaults to self.root if no value provided.
                attribute_string (str): The attribute to search for.
        Returns:
            attribute (Union[str, dict]): The string attribute if attribute_string is defined.
              If not, returns the full dict.
        """
        subtree = kwargs.pop('subtree', self.root)
        attribute_string = kwargs.pop('attribute_string', None)

        if attribute_string:
            try:
                element = subtree.find(xpath, namespaces=self.namespaces)
                attribute = element.attrib[attribute_string]
            except AttributeError:
                attribute = "Unknown"
        else:
            try:
                element = subtree.find(xpath, namespaces=self.namespaces)
                attribute = dict(element.attrib)
            except AttributeError:
                attribute = "Unknown"

        return attribute

    def get_geo_info(self) -> dict:
        """
        Args:
            self
        Returns:
            geo_info(dict): A dict containing feature information for intepretation by KmlPlus.
        """
        func_dict = {'AirportHeliport': self.get_arp_coordinates, 'Navaid': self.get_navaid_coordinates,
                     'Airspace': self.get_airspace_coordinates,
                     'DesignatedPoint': self.get_designated_point_coordinates,
                     'RouteSegment': self.get_route_segment_coordinates}

        try:
            geo_info = func_dict[self.feature_type]()
        except KeyError:
            geo_info = None

        return geo_info

    def get_arp_coordinates(self) -> dict:
        """
        Args:
            self
        Returns:
            geo_dict(dict): A dictionary containing relevant information regarding the feature.
        """
        geo_dict = {
            'coordinates': self.get_first_value('.//aixm:ARP//gml:pos'),
            'elevation': self.get_first_value('.//aixm:fieldElevation'),
            'elevation_uom': self.get_first_value_attribute('.//aixm:fieldElevation', attribute_string='uom'),
            'name': f'{self.get_first_value(".//aixm:designator")}({self.get_first_value(".//aixm:name")})',
        }

        return geo_dict

    def get_navaid_coordinates(self):
        """
        Args:
            self
        Returns:
            geo_dict(dict): A dictionary containing relevant information regarding the feature.
        """
        geo_dict = {
            'coordinates': self.get_first_value('.//aixm:location//gml:pos'),
            'elevation': self.get_first_value('.//aixm:location//aixm:elevation'),
            'elevation_uom': self.get_first_value_attribute('.//aixm:location//aixm:elevation',
                                                            attribute_string='uom'),
            'name': f'{self.get_first_value(".//aixm:designator")}({self.get_first_value(".//aixm:name")})' \
                    f' {self.get_first_value(".//aixm:type")}'
        }

        return geo_dict

    def get_designated_point_coordinates(self):
        """
        Args:
            self
        Returns:
            geo_dict(dict): A dictionary containing relevant information regarding the feature.
        """
        geo_dict = {
            'coordinates': self.get_first_value('.//aixm:location//gml:pos')
        }

        return geo_dict

    def get_airspace_coordinates(self):
        """
        Args:
            self
        Returns:
            geo_dict(dict): A dictionary containing relevant information regarding the feature.
        """

        crs = self.get_crs()
        root = self.root.findall('.//aixm:theAirspaceVolume//aixm:horizontalProjection//gml:segments',
                                 namespaces=self.namespaces)

        coordinate_string = ''
        for location in root:
            unpacked_gml = self.unpack_gml(location.getchildren(), crs=crs)
            coordinate_string += unpacked_gml

        geo_dict = {
            'upper_layer': self.get_first_value('.//aixm:theAirspaceVolume//aixm:upperLimit'),
            'upper_layer_uom': self.get_first_value_attribute('.//aixm:theAirspaceVolume//aixm:upperLimit',
                                                              attribute_string='uom'),
            'lower_layer': self.get_first_value('.//aixm:theAirspaceVolume//aixm:lowerLimit'),
            'lower_layer_uom': self.get_first_value_attribute('.//aixm:theAirspaceVolume//aixm:lowerLimit',
                                                              attribute_string='uom'),
            'name': f"{self.get_first_value('.//aixm:designator')} {self.get_first_value('.//aixm:name')}",
            'coordinate_string': coordinate_string
        }

        return geo_dict

    def get_crs(self):
        """
        Args:
            self
        Returns:
            crs(str): A string of 'Anticlockwise' or 'Clockwise' depending upon the CRS
            applied and the start and end angles
        """
        crs = self.get_first_value_attribute('.//aixm:Surface', attribute_string='srsName')
        split = crs.split(':')[-1]
        if split == '4326':
            crs = '4326'
        elif split == 'CRS84':
            crs = 'CRS84'
        else:
            raise TypeError(print('Only CRS84 and ESPG::4326 supported.'))

        return crs

    def get_route_segment_coordinates(self):
        """
        Args:
            self
        Returns:
            geo_dict(dict): A dictionary containing relevant information regarding the feature.
        """
        coordinate_string = ''
        root = self.root.findall('.//aixm:curveExtent//gml:segments', namespaces=self.namespaces)
        for location in root:
            coordinate_string += self.unpack_gml(location.getchildren())

        geo_dict = {
            'coordinate_string': coordinate_string
        }

        return geo_dict

    def unpack_gml(self, location: etree.Element, **kwargs: str) -> str:
        """
        Args:
            location(etree.Element): etree.Element containing specific aixm tags containing geographic information
            kwargs(str): crs=None the CRS to be used for determining arc directions for ArcByCenterPoint.
        Returns:
            coordinate_string(str): A coordinate string
        """
        crs = kwargs.pop('crs', None)
        coordinate_list = []
        for child in location:
            tag = child.tag.split('}')[-1]
            if tag == 'CircleByCenterPoint':
                coordinate_list.append(self.unpack_circle(child))
            elif tag == 'GeodesicString' or tag == 'LineStringSegment':
                points = child.findall('.//gml:pointProperty', namespaces=self.namespaces)
                for point in points:
                    coordinate_list.append(self.unpack_geodesic_string(point))
            elif tag == 'ArcByCenterPoint':
                coordinate_list.append(self.unpack_arc(child, crs))

            coordinate_string = ', '.join(coordinate_list)

        return coordinate_string

    def unpack_arc(self, location: etree.Element, crs: str) -> str:
        """
        Args:
            location(etree.Element): etree.Element containing specific aixm tags containing geographic information
            crs(str): CRS to be used for determining arc directions for ArcByCenterPoint.
        Returns:
            coordinate_string(str): A coordinate string
        """
        centre = self.get_first_value('.//gml:pos', subtree=location)
        start_angle = self.get_first_value('.//gml:startAngle', subtree=location)
        end_angle = self.get_first_value('.//gml:endAngle', subtree=location)
        # Pyproj uses metres, we will have to convert for distance
        radius = self.get_first_value('.//gml:radius', subtree=location)
        radius_uom = self.get_first_value_attribute('.//gml:radius', subtree=location, attribute_string='uom')
        crs = crs

        conversion_dict = {'FT': 0.3048, '[nmi_i]': 1852, 'MI': 1609.4, 'KM': 1000}

        if radius_uom != 'M':
            radius = float(radius) * conversion_dict[radius_uom]

        lat = centre.split(' ')[0]
        lon = centre.split(' ')[1]

        start_coord = Geod(ellps='WGS84').fwd(lon, lat, start_angle, radius)
        end_coord = Geod(ellps='WGS84').fwd(lon, lat, end_angle, radius)

        coordinate_string = f'start={round(start_coord[1], 5)} {round(start_coord[0], 5)},' \
                            f' end={round(end_coord[1], 5)} {round(end_coord[0], 5)}, centre={centre},' \
                            f' direction={self.determine_arc_direction(float(start_angle), float(end_angle), crs)}'

        return coordinate_string

    def determine_arc_direction(self, start_angle: float, end_angle: float, crs: str) -> str:
        """
        Args:
            start_angle(float): Start angle of the arc from it's centre point.
            end_angle(float): End angle of the arc from it's centre point.
            crs(str): The CRS being used by the AIXM feature.
        Returns:
            direction(str): Clockwise or Anticlockwise
        """
        if crs == '4326':
            if start_angle < end_angle:
                direction = 'clockwise'
            else:
                direction = 'anticlockwise'
        elif crs == 'CRS84':
            if start_angle < end_angle:
                direction = 'anticlockwise'
            else:
                direction = 'clockwise'
        else:
            raise TypeError(print('Only ESPG::4326 and CRS84 are supported.'))

        return direction

    def unpack_geodesic_string(self, location: etree.Element) -> str:
        """
        Args:
            location(etree.Element): etree.Element containing specific aixm tags containing geographic information
        Returns:
            coordinate_string(str): A coordinate string.
        """

        coordinate_string = self.get_first_value('.//aixm:Point//gml:pos', subtree=location)

        return coordinate_string

    def unpack_circle(self, location: etree.Element) -> str:
        """
            Args:
                location(etree.Element): etree.Element containing specific aixm tags containing geographic information
            Returns:
                coordinate_string(str): A coordinate string
        """
        centre = self.get_first_value('.//gml:pos', subtree=location)
        radius = self.get_first_value('.//gml:radius', subtree=location)
        radius_uom = self.get_first_value_attribute('.//gml:radius', subtree=location, attribute_string='uom')

        coordinate_string = f'{centre}, {radius} {radius_uom}'

        return coordinate_string


if __name__ == '__main__':
    file_loc = Path().absolute().joinpath('..', Path('test_data/test.xml'))
    AixmGeo(file_loc).extract_geo_info()
