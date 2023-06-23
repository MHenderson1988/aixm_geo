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

    def get_field_elevation(self):
        elevation = self.get_first_value('.//aixm:fieldElevation')
        elevation_uom = self.get_first_value_attribute('.//aixm:fieldElevation', attribute_string='uom')

        if elevation == 'Unknown':
            elevation = 0
            elevation_uom = 'M'

        return elevation, elevation_uom

    def get_vertical_extent(self):
        elevation = self.get_first_value('.//aixm:elevation')
        elevation_uom = self.get_first_value_attribute('.//aixm:elevation', attribute_string='uom')

        if elevation == 'Unknown':
            elevation = 0
            elevation_uom = 'M'

        return elevation, elevation_uom

    def get_crs(self):
        """
        Parses the CRS from the AirspaceGeometryComponent parent tag and returns the CRS as a string.
        Args:
            self
        Returns:
            crs(str): A string of 'Anticlockwise' or 'Clockwise' depending upon the CRS
            applied and the start and end angles
        """
        crs = self._timeslice[-1].xpath(".//*[@srsName]", namespaces=NAMESPACES)[0]

        split = crs.get("srsName").split(':')[-1]
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

    def get_airspace_elevation(self):
        lower_layer = self.get_first_value('.//aixm:theAirspaceVolume//aixm:lowerLimit')
        lower_layer_uom = self.get_first_value_attribute('.//aixm:theAirspaceVolume//aixm:lowerLimit',
                                                         attribute_string='uom')
        upper_layer = self.get_first_value('.//aixm:theAirspaceVolume//aixm:upperLimit')
        upper_layer_uom = self.get_first_value_attribute('.//aixm:theAirspaceVolume//aixm:upperLimit',
                                                         attribute_string='uom')

        if lower_layer == 'Unknown':
            lower_layer = 0.0
            lower_layer_uom = 'M'
        if upper_layer == 'Unknown':
            upper_layer = 0.0
            upper_layer_uom = 'M'

        return lower_layer, lower_layer_uom, upper_layer, upper_layer_uom

    def get_coordinate_list(self, subroot):
        """
        Parses the LXML etree._Element object and returns a list of coordinate strings.
        Args:
            subroot: LXML etree._Element object

        Returns:
            unpacked_gml(list[str]): A list of coordinate strings

        """
        unpacked_gml = None
        for location in subroot:
            try:
                unpacked_gml = self.unpack_gml(location)
            except TypeError:
                print('Coordinates can only be extracted from an LXML etree._Element object.')

        for x in unpacked_gml:
            x.strip("r'\'")

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
        for x in self.extract_pos_and_poslist(location):
            coordinate_list.append(x)
        return coordinate_list

    def extract_pos_and_poslist(self, location):
        """
        Args:
            self
        Returns:
            coordinate_string(str): A coordinate string
        """
        for child in location.iterdescendants():
            tag = child.tag.split('}')[-1]
            if tag == 'GeodesicString' or tag == 'ElevatedPoint':
                for x in self.unpack_geodesic_string(child):
                    yield x
            elif tag == 'CircleByCenterPoint':
                yield self.unpack_circle(child)
            elif tag == 'ArcByCenterPoint':
                yield self.unpack_arc(child)

    def unpack_geodesic_string(self, location):
        for child in location.iterdescendants():
            tag = child.tag.split('}')[-1]
            if tag == 'pos':
                yield child.text
            elif tag == 'posList':
                for x in self.unpack_pos_list(child.text):
                    yield x

    def unpack_pos_list(self, string_to_manipulate):
        split = string_to_manipulate.split(' ')
        if len(split) > 1:
            for i in range(len(split) - 1):
                if i < len(split) and i % 2 == 0:
                    new_string = f'{split[i]} {split[i + 1]}'
                    yield new_string
        else:
            yield string_to_manipulate

    def unpack_arc(self, location: etree.Element) -> str:
        """
        Args:
            location(etree.Element): etree.Element containing specific aixm tags containing geographic information
            crs(str): CRS to be used for determining arc directions for ArcByCenterPoint.
        Returns:
            coordinate_string(str): A coordinate string
        """
        centre = self.get_arc_centre_point(location).strip()
        start_angle = self.get_first_value('.//gml:startAngle', subtree=location)
        end_angle = self.get_first_value('.//gml:endAngle', subtree=location)
        # Pyproj uses metres, we will have to convert for distance
        radius = self.get_first_value('.//gml:radius', subtree=location)
        radius_uom = self.get_first_value_attribute('.//gml:radius', subtree=location, attribute_string='uom')

        conversion_dict = {'ft': 0.3048, 'NM': 1852, '[nmi_i]': 1852, 'mi': 1609.4, 'km': 1000}

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

    def get_arc_centre_point(self, location):
        centre = self.get_first_value('.//gml:pos', subtree=location)

        # If none, check for gml:posList instead
        if centre == 'Unknown':
            centre = self.get_first_value('.//gml:posList', subtree=location)

        return centre

    def get_circle_centre_point(self, location):
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
        centre = self.get_circle_centre_point(location)
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
