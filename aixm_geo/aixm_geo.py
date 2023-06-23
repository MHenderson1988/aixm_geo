from pathlib import Path

from kmlplus import kml

import util as util
from factory import AixmFeatureFactory


class AixmGeo:
    __slots__ = ('aixm_file', 'output_path', 'file_name')

    def __init__(self, aixm_file, output_path, file_name):
        self.aixm_file = aixm_file
        self.output_path = output_path
        self.file_name = file_name

    def build_kml(self):
        kml_obj = kml.KmlPlus(output=self.output_path, file_name=self.file_name)
        self.draw_features(kml_obj)

    def draw_features(self, kml_obj):
        for aixm_feature_obj in AixmFeatureFactory(self.aixm_file):
            aixm_feature_dict = aixm_feature_obj.get_geographic_information()
            if aixm_feature_dict:
                geometry_type = util.determine_geometry_type(aixm_feature_dict)
                if geometry_type == 'cylinder':
                    self.draw_cylinder(aixm_feature_dict, kml_obj)
                elif geometry_type == 'point':
                    if aixm_feature_dict['type'] == 'VerticalStructure':
                        self.draw_vertical_structure_point(aixm_feature_dict, kml_obj)
                    else:
                        kml_obj.point(aixm_feature_dict["coordinates"], fol=aixm_feature_dict['name'],
                                      point_name=aixm_feature_dict['name'])
                elif geometry_type == 'polyhedron':
                    self.draw_airspace(aixm_feature_dict, kml_obj)
                print(aixm_feature_dict)

            else:
                pass

    def draw_vertical_structure_point(self, aixm_feature_dict, kml_obj):
        kml_obj.point(aixm_feature_dict["coordinates"], uom=aixm_feature_dict['elevation_uom'],
                      fol=aixm_feature_dict['name'], point_name=aixm_feature_dict['name'],
                      altitude_mode='relativeToGround', extrude=1)

    def draw_airspace(self, aixm_feature_dict, kml_obj):
        kml_obj.polyhedron(aixm_feature_dict["coordinates"],
                           aixm_feature_dict["coordinates"],
                           upper_layer=float(aixm_feature_dict['upper_layer']),
                           lower_layer=float(aixm_feature_dict['lower_layer']),
                           uom=aixm_feature_dict['lower_layer_uom'], fol=aixm_feature_dict['name'],
                           altitude_mode=util.altitude_mode(aixm_feature_dict))

    def draw_cylinder(self, aixm_feature_dict, kml_obj):

        coordinates = aixm_feature_dict['coordinates'][0].split(',')[0].strip()
        radius = aixm_feature_dict['coordinates'][0].split(',')[1].split('=')[-1]
        radius_uom = util.switch_radius_uom(aixm_feature_dict['coordinates'][0].split(',')[2].split('=')[-1])
        lower_layer = aixm_feature_dict['lower_layer']
        upper_layer = aixm_feature_dict['upper_layer']

        kml_obj.cylinder(coordinates, float(radius),
                         radius_uom=radius_uom, lower_layer=float(lower_layer),
                         upper_layer=float(upper_layer),
                         fol=aixm_feature_dict['name'], lower_layer_uom=aixm_feature_dict['lower_layer_uom'],
                         upper_layer_uom=aixm_feature_dict['upper_layer_uom'],
                         altitude_mode=util.altitude_mode(aixm_feature_dict))


if __name__ == '__main__':
    file_loc = Path().absolute().joinpath('..', Path('test_data/donlon.xml'))
    output = Path().absolute()
    AixmGeo(file_loc, output, 'test_kml.kml').build_kml()
