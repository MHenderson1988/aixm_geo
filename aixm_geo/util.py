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


def convert_elevation(z_value: str, current_uom: str) -> float:
    if z_value == 'GND':
        current_uom = 'M'
        z_value = 0.0

    if z_value == 'UNL':
        current_uom = 'M'
        z_value = 18288.00  # 60,000 ft in metres

    if current_uom == 'FL':
        current_uom = 'M'
        z_value = (float(z_value) * 100) * .3048  # 1 ft in metres

    return z_value, current_uom


def altitude_mode(aixm_dict):
    altitude_mode = 'absolute'
    if aixm_dict['upper_layer_reference'] == 'SFC':
        altitude_mode = 'relativetoground'
    return altitude_mode


def switch_radius_uom(radius_uom):
    if radius_uom == '[nmi_i]':
        radius_uom = 'NM'
    return radius_uom


def determine_geometry_type(aixm_feature_dict):
    geometry_type = None
    if aixm_feature_dict['type'] == 'RouteSegment':
        geometry_type = 'LineString'

    elif aixm_feature_dict['type'] == 'VerticalStructure':
        if len(aixm_feature_dict['coordinates']) > 1:
            aixm_feature_dict['lower_layer'] = 0.0
            aixm_feature_dict['upper_layer'] = aixm_feature_dict['elevation']
            geometry_type = 'Polygon'
        else:
            geometry_type = 'point'
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
