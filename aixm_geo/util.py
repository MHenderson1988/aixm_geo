from datetime import datetime

from aixm_geo.settings import NAMESPACES


def get_feature_type(timeslices) -> str:
    try:
        feature_type = timeslices[-1].find('.//', NAMESPACES).tag.split('}')[-1].split('T')[0]
    except IndexError:
        feature_type = "Unknown"
    return feature_type


def parse_timeslice(subroot) -> list:
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
        timeslices.sort(key=lambda x: datetime.strptime(
            x.find('.//{http://www.aixm.aero/schema/5.1}versionBegin').text.split('T')[0],
            "%Y-%m-%d"))
    return timeslices
