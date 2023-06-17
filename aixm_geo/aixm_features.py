from base import SinglePointAixm, MultiPointAixm
from interfaces import IAixmFeature
from settings import NAMESPACES


class AirportHeliport(SinglePointAixm, IAixmFeature):
    def __init__(self, root):
        super().__init__(root)

    def get_geographic_information(self):
        """
        Args:
            self
        Returns:
            geo_dict(dict): A dictionary containing relevant information regarding the feature.
        """

        elevation, elevation_uom = self.get_elevation()
        geo_dict = {
            'type': 'AirportHeliport',
            'coordinates': [f"{self.get_first_value('.//aixm:ARP//gml:pos')} "
                            f"{elevation}"],
            'elevation': elevation,
            'elevation_uom': elevation_uom,
            'name': f'{self.get_first_value(".//aixm:designator")} ({self.get_first_value(".//aixm:name")})',
        }

        return geo_dict


class NavaidComponent(SinglePointAixm, IAixmFeature):
    def __init__(self, root):
        super().__init__(root)

    def get_geographic_information(self):
        """
        Args:
            self
        Returns:
            geo_dict(dict): A dictionary containing relevant information regarding the feature.
        """
        elevation, elevation_uom = self.get_elevation()

        geo_dict = {
            'type': 'NavaidComponent',
            'coordinates': [f"{self.get_first_value('.//aixm:location//gml:pos')}"
                            f" {elevation}"],
            'elevation': elevation,
            'elevation_uom': elevation_uom,
            'name': f'{self.get_first_value(".//aixm:designator")}({self.get_first_value(".//aixm:name")})' \
                    f' {self.get_first_value(".//aixm:type")}'
        }

        return geo_dict


class DesignatedPoint(SinglePointAixm, IAixmFeature):
    def __init__(self, root):
        super().__init__(root)

    def get_geographic_information(self):
        """
        Args:
            self
        Returns:
            geo_dict(dict): A dictionary containing relevant information regarding the feature.
        """
        geo_dict = {
            'type': 'DesignatedPoint',
            'name': self.get_first_value('.//aixm:name'),
            'coordinates': [self.get_first_value('.//aixm:location//gml:pos')]
        }

        return geo_dict


class RouteSegment(MultiPointAixm, IAixmFeature):
    def __init__(self, root):
        super().__init__(root)

    def get_geographic_information(self) -> dict:
        """
        Args:
            self
        Returns:
            geo_dict(dict): A dictionary containing relevant information regarding the feature.
        """
        coordinate_list = []
        root = self._root.iterfind('.//aixm:curveExtent', namespaces=NAMESPACES)
        for location in root:
            for x in self.extract_pos_and_poslist(location):
                coordinate_list.append(x)

        geo_dict = {
            'type': 'RouteSegment',
            'coordinates': coordinate_list,
            # TODO add name for route segments
        }

        return geo_dict


class Airspace(MultiPointAixm, IAixmFeature):
    def __init__(self, root):
        super().__init__(root)

    def get_geographic_information(self):
        """
        Args:
            self
        Returns:
            geo_dict(dict): A dictionary containing relevant information regarding the feature.
        """
        subroot = self._root.findall('.//aixm:theAirspaceVolume//aixm:horizontalProjection',
                                     namespaces=NAMESPACES)

        coordinate_list = self.get_coordinate_list(subroot)

        lower_layer, lower_layer_uom, upper_layer, upper_layer_uom = self.get_elevation()

        geo_dict = {
            'type': 'Airspace',
            'upper_layer': upper_layer,
            'upper_layer_uom': upper_layer_uom,
            'lower_layer': lower_layer,
            'lower_layer_uom': lower_layer_uom,
            'name': f"{self.get_first_value('.//aixm:designator')} {self.get_first_value('.//aixm:name')}",
            'coordinates': coordinate_list,
        }

        return geo_dict
