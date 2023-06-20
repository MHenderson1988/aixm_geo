from datetime import datetime

from lxml.etree import _Element

from settings import NAMESPACES


def get_feature_type(timeslices: list) -> str:
    """
    Returns the type of AIXM feature from the most recent timeslice

    Args:
        timeslices (list): A list of one or more AIXM timeslice

    Returns:
         feature_type (str): The AIXM feature type.
    """
    try:
        feature_type = timeslices[-1].find('.', NAMESPACES).tag
        feature_type = feature_type.split('}')[-1].split('T')[0]
    except IndexError:
        feature_type = "Unknown"
    return feature_type


def parse_timeslice(subroot: _Element) -> list:
    """Looks at the timeslices contained within the feature and arranges them in time order (oldest to newest).

    Returns:
        timeslices (list):
            A list of timeslices in chronological order.

    """
    # Get a list of timeslices
    try:
        timeslices = subroot.findall('.//aixm:timeSlice', NAMESPACES)
    except IndexError:
        timeslices = None
    # Don't bother to sort if there is only one timeslice
    if len(timeslices) > 1:
        try:
            timeslices.sort(key=lambda x: datetime.strptime(
                x.find('.//{http://www.aixm.aero/schema/5.1}versionBegin').text.split('T')[0],
                "%Y-%m-%d"))
        except AttributeError:
            pass
    return timeslices


def convert_elevation(aixm_feature_dict):
    if aixm_feature_dict['lower_layer_uom'] == 'FL':
        aixm_feature_dict['lower_layer_uom'] = 'FT'
        aixm_feature_dict['lower_layer'] = float(aixm_feature_dict['lower_layer']) * 100

    if aixm_feature_dict['lower_layer'] == 'GND':
        aixm_feature_dict['lower_layer_uom'] = 'M'
        aixm_feature_dict['lower_layer'] = 0.0

    if aixm_feature_dict['upper_layer_uom'] == 'FL':
        aixm_feature_dict['upper_layer_uom'] = 'FT'
        aixm_feature_dict['upper_layer'] = float(aixm_feature_dict['upper_layer']) * 100

    if aixm_feature_dict['upper_layer'] == 'UNL':
        aixm_feature_dict['upper_layer_uom'] = 'M'
        aixm_feature_dict['upper_layer'] = 18288.00 # 60,000 ft in metres

    return aixm_feature_dict


def switch_radius_uom(radius_uom):
    if radius_uom == '[nmi_i]':
        radius_uom = 'NM'
    return radius_uom


def determine_geometry_type(aixm_feature_dict):
    geometry_type = None
    if aixm_feature_dict['type'] == 'RouteSegment':
        geometry_type = 'LineString'

    elif len(aixm_feature_dict["coordinates"]) == 1:
        if 'radius=' in aixm_feature_dict['coordinates'][0]:
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
