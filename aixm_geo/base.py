from typing import Union

from lxml import etree
from pyproj import Geod

import util as util
from settings import NAMESPACES


class SinglePointAixm:
    """
    A base class for all AIXM features who's representative geographic information is held in a single point.

    Examples -

    AirportHeliport - Geographic information is a single point (ARP)
    DesignatedPoint - A single geographic point

    Args:
        root (
    """

    def __init__(self, root):
        __slots__ = ['_root', '_timeslice']
        self._root = root
        self._timeslice = util.parse_timeslice(self._root)

    def get_first_value(self, xpath: str, **kwargs: etree.Element) -> str:
        """Returns the first matching text value found within the subtree which match the Xpath provided.

        Args:
            xpath (str): Valid Xpath string for the value to try and find.
            **kwargs:
                subtree(etree.Element): The subtree to search.  Defaults to self.root if no value provided.
        Returns:
            value (str): String value of the tag found.
        """
        subtree = kwargs.pop('subtree', self._root)
        try:
            value = subtree.find(xpath, namespaces=NAMESPACES).text
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
        subtree = kwargs.pop('subtree', self._root)
        try:
            values = subtree.findall(xpath, namespaces=NAMESPACES)
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
        subtree = kwargs.pop('subtree', self._root)
        attribute_string = kwargs.pop('attribute_string', None)

        if attribute_string:
            try:
                element = subtree.find(xpath, namespaces=NAMESPACES)
                attribute = element.attrib[attribute_string]
            except AttributeError:
                attribute = "Unknown"
        else:
            try:
                element = subtree.find(xpath, namespaces=NAMESPACES)
                attribute = dict(element.attrib)
            except AttributeError:
                attribute = "Unknown"

        return attribute

    def get_elevation(self):
        elevation = self.get_first_value('.//aixm:fieldElevation')
        elevation_uom = self.get_first_value_attribute('.//aixm:fieldElevation', attribute_string='uom')

        if elevation == 'Unknown':
            elevation = 0
            elevation_uom = 'FT'

        return elevation, elevation_uom

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


class MultiPointAixm(SinglePointAixm):
    """
    Extends SinglePointAixm for use with features who's geographic representation is often represented by multiple
    points which make up polygons etc.

    Examples

    Airspace
    RouteSegment
    """

    def __init__(self, root):
        super().__init__(root)

    def get_coordinate_list(self, subroot):
        unpacked_gml = None
        for location in subroot:
            try:
                unpacked_gml = self.unpack_gml(location.iterdescendants())
            except TypeError:
                print('Coordinates can only be extracted from an LXML etree._Element object.')
        return unpacked_gml

    def unpack_gml(self, location: etree.Element) -> list[str]:
        """
        Args:
            location(etree.Element): etree.Element containing specific aixm tags containing geographic information
            kwargs(str): crs=None the CRS to be used for determining arc directions for ArcByCenterPoint.
        Returns:
            coordinate_string(str): A coordinate string
        """
        coordinate_list = []
        for child in location:
            tag = child.tag.split('}')[-1]
            if tag == 'CircleByCenterPoint':
                next_coordinate = self.unpack_circle(child)
                coordinate_list.append(next_coordinate)
            elif tag == 'Ring':
                pos_iter = child.iterfind('.//gml:posList', namespaces=NAMESPACES)
                for posList in pos_iter:
                    string_list = self.process_geodesic_string(posList.text)
                    coordinate_list.extend(string_list)
            elif tag == 'LineStringSegment':
                points = child.findall('.//gml:pointProperty', namespaces=NAMESPACES)
                for point in points:
                    next_coordinate = self.unpack_linestring(point)
                    coordinate_list.append(next_coordinate)
            elif tag == 'ArcByCenterPoint':
                next_coordinate = self.unpack_arc(child)
                coordinate_list.append(next_coordinate)

        return coordinate_list

    def unpack_curve(self, location):
        coordinate_string = ""
        for child in location.findall('.//gml:curveMember', namespaces=NAMESPACES):
            coordinate_string += child.find('.//gml:posList', namespaces=NAMESPACES).text
        return coordinate_string

    def process_geodesic_string(self, string_to_manipulate):
        split = string_to_manipulate.split(' ')
        coordinate_list = []
        if len(split) > 2:
            coordinate_list.append(f'{split[0]} {split[1]}')
            for i in range(len(split)):
                if i < len(split) and i % 2 == 0 and i != 0:
                    new_string = f'{split[i]} {split[i + 1]}'
                    coordinate_list.append(new_string)
        else:
            coordinate_list.append(string_to_manipulate)

        return coordinate_list

    def unpack_arc(self, location: etree.Element) -> str:
        """
        Args:
            location(etree.Element): etree.Element containing specific aixm tags containing geographic information
            crs(str): CRS to be used for determining arc directions for ArcByCenterPoint.
        Returns:
            coordinate_string(str): A coordinate string
        """
        centre = self.get_centre(location).strip()
        start_angle = self.get_first_value('.//gml:startAngle', subtree=location)
        end_angle = self.get_first_value('.//gml:endAngle', subtree=location)
        # Pyproj uses metres, we will have to convert for distance
        radius = self.get_first_value('.//gml:radius', subtree=location)
        radius_uom = self.get_first_value_attribute('.//gml:radius', subtree=location, attribute_string='uom')

        conversion_dict = {'ft': 0.3048, '[nmi_i]': 1852, 'mi': 1609.4, 'km': 1000}

        if radius_uom != 'm':
            radius = float(radius) * conversion_dict[radius_uom]

        lat = centre.split(' ')[0]
        lon = centre.split(' ')[1]

        start_coord = Geod(ellps='WGS84').fwd(lon, lat, start_angle, radius)
        end_coord = Geod(ellps='WGS84').fwd(lon, lat, end_angle, radius)

        coordinate_string = f'start={round(start_coord[1], 5)} {round(start_coord[0], 5)},' \
                            f' end={round(end_coord[1], 5)} {round(end_coord[0], 5)}, centre={centre},' \
                            f' direction={self.determine_arc_direction(float(start_angle), float(end_angle))}'

        return coordinate_string

    def get_centre(self, location):
        centre = self.get_first_value('.//gml:pos', subtree=location)

        # If none, check for gml:posList instead
        if centre == 'Unknown':
            centre = self.get_first_value('.//gml:posList', subtree=location)

        return centre

    def determine_arc_direction(self, start_angle: float, end_angle: float) -> str:
        """
        Args:
            start_angle(float): Start angle of the arc from it's centre point.
            end_angle(float): End angle of the arc from it's centre point.
            crs(str): The CRS being used by the AIXM feature.
        Returns:
            direction(str): Clockwise or Anticlockwise
        """
        crs = self.get_crs()
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

    def unpack_linestring(self, location: etree.Element) -> str:
        """
        Args:
            location(etree.Element): etree.Element containing specific aixm tags containing geographic information
        Returns:
            coordinate_string(str): A coordinate string.
        """

        coordinate_string = self.get_first_value('.//aixm:Point//gml:pos', subtree=location)
        if coordinate_string == 'Unknown':
            coordinate_string = self.get_first_value('.//aixm:Point//gml:posList', subtree=location)

        return coordinate_string

    def unpack_circle(self, location: etree.Element) -> str:
        """
            Args:
                location(etree.Element): etree.Element containing specific aixm tags containing geographic information
            Returns:
                coordinate_string(str): A coordinate string
        """
        centre = self.get_centre(location)
        radius = self.get_first_value('.//gml:radius', subtree=location)
        radius_uom = self.get_first_value_attribute('.//gml:radius', subtree=location, attribute_string='uom')

        coordinate_string = f'{centre}, radius={radius}, radius_uom={radius_uom}'

        return coordinate_string

    def get_elevation(self):
        lower_layer = self.get_first_value('.//aixm:theAirspaceVolume//aixm:lowerLimit')
        lower_layer_uom = self.get_first_value_attribute('.//aixm:theAirspaceVolume//aixm:lowerLimit',
                                                         attribute_string='uom')
        upper_layer = self.get_first_value('.//aixm:theAirspaceVolume//aixm:upperLimit')
        upper_layer_uom = self.get_first_value_attribute('.//aixm:theAirspaceVolume//aixm:upperLimit',
                                                         attribute_string='uom')

        if lower_layer == 'Unknown':
            lower_layer = 0
            lower_layer_uom = 'FT'
        if upper_layer == 'Unknown':
            upper_layer = 0
            upper_layer_uom = 'FT'

        return lower_layer, lower_layer_uom, upper_layer, upper_layer_uom
