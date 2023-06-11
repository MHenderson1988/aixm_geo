from pathlib import Path

from kmlplus import kml


class AixmGeo:

    def build_kml(self, file_name, output_path):
        kml_obj = kml.KmlPlus(output=output_path, file_name=file_name)
        self.draw_features(kml_obj)

    def draw_features(self, kml_obj):
        for aixm_feature_dict in self.geo_info:
            if aixm_feature_dict:
                geometry_type = self.determine_geometry_type(aixm_feature_dict)

                if geometry_type == 'cylinder':
                    kml_obj.cylinder(aixm_feature_dict["coordinates"], aixm_feature_dict["radius"],
                                     uom=aixm_feature_dict["radius_uom"])
                elif geometry_type == 'point':
                    kml_obj.point(aixm_feature_dict["coordinates"])

                elif geometry_type == 'polyhedron':
                    kml_obj.polyhedron(aixm_feature_dict["coordinates"])

                return geometry_type
            else:
                pass

    def determine_geometry_type(self, aixm_feature_dict):
        geometry_type = None
        if aixm_feature_dict['type'] == 'RouteSegment':
            geometry_type = 'LineString'

        elif len(aixm_feature_dict["coordinates"]) == 1:
            if 'start=' in aixm_feature_dict["coordinates"][0]:
                if aixm_feature_dict["upper_layer"]:
                    geometry_type = 'cylinder'
            else:
                geometry_type = 'point'

        elif len(aixm_feature_dict["coordinates"]) == 2:
            for coordinate in aixm_feature_dict["coordinates"]:
                if 'start=' in coordinate:
                    return 'polyhedron'
            if geometry_type is None:
                return 'linestring'

        elif len(aixm_feature_dict["coordinates"]) > 2:
            if aixm_feature_dict["upper_layer"]:
                geometry_type = 'polyhedron'
            else:
                geometry_type = 'polygon'

        return geometry_type


if __name__ == '__main__':
    file_loc = Path().absolute().joinpath('..', Path('test_data/test.xml'))
    AixmGeo(file_loc).extract_geo_info()
