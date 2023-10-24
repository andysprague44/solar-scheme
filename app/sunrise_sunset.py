import requests
from requests.models import PreparedRequest
from dateutil import parser
import datetime

def get_lat_lon_from_address(
    street: str = None,
    city: str = None,
    county: str = None,
    state: str = None,
    country: str = None,
    postalcode: str = None):
    """
    Get latitude and longitde from an address, using the service at https://geocode.maps.co/. All arguments are optional.

    For England, 'state' should be 'England', and country 'UK'. Possibly the same for other UK and european coutries.
    """
    params = {key: value for key, value in locals().items() if value is not None}
    res = __get_json_from_url('https://geocode.maps.co/search', params)
    lat = res[0]['lat']
    lon = res[0]['lon']
    return lat, lon


def get_monthly_sunrise_sunset(year: int, lat: float, lon: float):
    """
    Get sunrise/sunset info for the 1st of each month of the given year

    Args:
        - year (int): year to get monthly data for
        - lat (float): latitude
        - lon (float): longitude

    Returns:
        Tuple of timedeltas (sunrises, sunsets), containing only the hour and minute portion of the sunrise/sunset.
    """
    sunrise = []
    sunset = []
    for month in range(1, 13):
        res = __get_json_from_url('https://api.sunrisesunset.io/json', {'lat': lat, 'lng': lon, 'date': f'{year}-{month}-1'})
        sunrise_datetime = parser.parse(res['results']['sunrise'])
        sunrise.append(datetime.timedelta(hours = sunrise_datetime.hour, minutes=sunrise_datetime.minute))
        sunset_datetime = parser.parse(res['results']['sunset'])
        sunset.append(datetime.timedelta(hours = sunset_datetime.hour, minutes=sunset_datetime.minute))
    return sunrise, sunset


def __get_json_from_url(url, params):
    req = PreparedRequest()
    req.prepare_url(url, params)
    res = requests.get(req.url).json()
    return res
