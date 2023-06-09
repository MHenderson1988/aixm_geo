from aixm_geo.base import SinglePointAixm, MultiPointAixm
from aixm_geo.interfaces import IAixmFeature
from aixm_geo.settings import NAMESPACES


class AirportHeliport(SinglePointAixm, IAixmFeature):
    def __init__(self, root, timeslice):
        super().__init__(root, timeslice)

    def get_geographic_information(self):
        """
        Args:
            self
        Returns:
            geo_dict(dict): A dictionary containing relevant information regarding the feature.
        """
        geo_dict = {
            'type': 'AirportHeliport',
            'coordinates': [f"{self.get_first_value('.//aixm:ARP//gml:pos')} "
                            f"{self.get_first_value('.//aixm:fieldElevation')}"],
            'elevation': self.get_first_value('.//aixm:fieldElevation'),
            'elevation_uom': self.get_first_value_attribute('.//aixm:fieldElevation', attribute_string='uom'),
            'name': f'{self.get_first_value(".//aixm:designator")}({self.get_first_value(".//aixm:name")})',
        }

        return geo_dict


class NavaidComponent(SinglePointAixm, IAixmFeature):
    def __init__(self, root, timeslice):
        super().__init__(root, timeslice)

    def get_geographic_information(self):
        """
        Args:
            self
        Returns:
            geo_dict(dict): A dictionary containing relevant information regarding the feature.
        """
        geo_dict = {
            'type': 'NavaidComponent',
            'coordinates': [f"{self.get_first_value('.//aixm:location//gml:pos')}"
                            f" {self.get_first_value('.//aixm:location//aixm:elevation')}"],
            'elevation': self.get_first_value('.//aixm:location//aixm:elevation'),
            'elevation_uom': self.get_first_value_attribute('.//aixm:location//aixm:elevation',
                                                            attribute_string='uom'),
            'name': f'{self.get_first_value(".//aixm:designator")}({self.get_first_value(".//aixm:name")})' \
                    f' {self.get_first_value(".//aixm:type")}'
        }

        return geo_dict


class DesignatedPoint(SinglePointAixm, IAixmFeature):
    def __init__(self, root, timeslice):
        super().__init__(root, timeslice)

    def get_geographic_information(self):
        """
        Args:
            self
        Returns:
            geo_dict(dict): A dictionary containing relevant information regarding the feature.
        """
        geo_dict = {
            'type': 'DesignatedPoint',
            'coordinates': [self.get_first_value('.//aixm:location//gml:pos')]
        }

        return geo_dict


class RouteSegment(MultiPointAixm, IAixmFeature):
    def __init__(self, root, timeslice):
        super().__init__(root, timeslice)

    def get_geographic_information(self) -> dict:
        """
        Args:
            self
        Returns:
            geo_dict(dict): A dictionary containing relevant information regarding the feature.
        """
        coordinate_string = ''
        root = self._root.findall('.//aixm:curveExtent//gml:segments', namespaces=NAMESPACES)
        for location in root:
            next_coordinate = self.unpack_gml(location.getchildren())
            coordinate_string = ', '.join(next_coordinate)

        geo_dict = {
            'type': 'RouteSegment',
            'coordinates': coordinate_string
        }

        return geo_dict


class Airspace(MultiPointAixm, IAixmFeature):
    def __init__(self, root, timeslice):
        super().__init__(root, timeslice)

    def get_geographic_information(self):
        """
        Args:
            self
        Returns:
            geo_dict(dict): A dictionary containing relevant information regarding the feature.
        """
        subroot = self._root.findall('.//aixm:theAirspaceVolume//aixm:horizontalProjection//gml:segments',
                                     namespaces=NAMESPACES)

        coordinate_list = self.get_coordinate_list(subroot)

        geo_dict = {
            'type': 'Airspace',
            'upper_layer': self.get_first_value('.//aixm:theAirspaceVolume//aixm:upperLimit'),
            'upper_layer_uom': self.get_first_value_attribute('.//aixm:theAirspaceVolume//aixm:upperLimit',
                                                              attribute_string='uom'),
            'lower_layer': self.get_first_value('.//aixm:theAirspaceVolume//aixm:lowerLimit'),
            'lower_layer_uom': self.get_first_value_attribute('.//aixm:theAirspaceVolume//aixm:lowerLimit',
                                                              attribute_string='uom'),
            'name': f"{self.get_first_value('.//aixm:designator')} {self.get_first_value('.//aixm:name')}",
            'coordinates': coordinate_list
        }

        return geo_dict
