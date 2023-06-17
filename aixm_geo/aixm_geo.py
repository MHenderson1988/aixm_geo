from pathlib import Path

from kmlplus import kml

import util


class AixmGeo:
    def build_kml(self, file_name, output_path):
        kml_obj = kml.KmlPlus(output=output_path, file_name=file_name)
        self.draw_features(kml_obj)

    def draw_features(self, kml_obj):
        for aixm_feature_obj in AixmFeatureFactory(file_loc):
            aixm_feature_dict = aixm_feature_obj.get_geographic_information()
            if aixm_feature_dict:
                print(aixm_feature_dict)
                geometry_type = util.determine_geometry_type(aixm_feature_dict)
                if geometry_type == 'cylinder':
                    self.draw_cylinder(aixm_feature_dict, kml_obj)
                elif geometry_type == 'point':
                    kml_obj.point(aixm_feature_dict["coordinates"], fol=aixm_feature_dict['name'],
                                  point_name=aixm_feature_dict['name'])
                elif geometry_type == 'polyhedron':
                    if aixm_feature_dict['lower_layer_uom'] == 'FL':
                        kml_obj.polyhedron(aixm_feature_dict["coordinates"],
                                           # Convert to FL ie FL 95 x by 100 to get 9500 for correct conversion
                                           upper_layer=float(aixm_feature_dict['upper_layer']) * 100,
                                           lower_layer=float(aixm_feature_dict['lower_layer']) * 100,
                                           lower_layer_uom=aixm_feature_dict['lower_layer_uom'],
                                           upper_layer_uom=aixm_feature_dict['upper_layer_uom'],
                                           uom=aixm_feature_dict['lower_layer_uom'], fol=aixm_feature_dict['name'],
                                           altitude_mode='absolute')
                    else:
                        kml_obj.polyhedron(aixm_feature_dict["coordinates"],
                                           upper_layer=float(aixm_feature_dict['upper_layer']),
                                           lower_layer=float(aixm_feature_dict['lower_layer']),
                                           lower_layer_uom=aixm_feature_dict['lower_layer_uom'],
                                           upper_layer_uom=aixm_feature_dict['upper_layer_uom'],
                                           uom=aixm_feature_dict['lower_layer_uom'], fol=aixm_feature_dict['name'])

            else:
                pass

    def draw_cylinder(self, aixm_feature_dict, kml_obj):
        coordinates = aixm_feature_dict['coordinates'][0].split(',')[0].strip()
        radius = aixm_feature_dict['coordinates'][0].split(',')[1].split('=')[-1]
        radius_uom = aixm_feature_dict['coordinates'][0].split(',')[2].split('=')[-1]
        lower_layer = aixm_feature_dict['lower_layer']
        upper_layer = aixm_feature_dict['upper_layer']
        uom = aixm_feature_dict['lower_layer_uom']

        if radius_uom == '[nmi_i]':
            radius_uom = 'NM'

        if uom == 'FL':
            uom = 'FT'
            kml_obj.cylinder(coordinates, float(radius),
                             radius_uom=radius_uom, lower_layer=float(lower_layer),
                             upper_layer=float(upper_layer), uom=uom,
                             fol=aixm_feature_dict['name'], lower_layer_uom=aixm_feature_dict['lower_layer_uom'],
                             upper_layer_uom=aixm_feature_dict['upper_layer_uom'], altitude_mode='absolute')
        else:
            kml_obj.cylinder(coordinates, float(radius),
                             radius_uom=radius_uom, lower_layer=float(lower_layer), upper_layer=float(upper_layer),
                             uom=uom, lower_layer_uom=aixm_feature_dict['lower_layer_uom'],
                             upper_layer_uom=aixm_feature_dict['upper_layer_uom'],
                             fol=aixm_feature_dict['name'])


if __name__ == '__main__':
    from factory import AixmFeatureFactory

    file_loc = Path().absolute().joinpath('..', Path('test_data/3_23_delta.xml'))
    output = Path().absolute()
    AixmGeo().build_kml('test_kml.kml', output)
