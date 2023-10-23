from src import solar_scheme
from src import sunrise_sunset
import numpy as np
import datetime as datetime
import requests

def test_example():
    assert 1 == 1, "should be able to run tests"


def test_geo_coding():
    lat, lon = sunrise_sunset.get_lat_lon_from_address(city='coaley', county='gloucestershire', country='UK')

    #test reverse geo-coding gives us a hit
    res = requests.get(f'https://geocode.maps.co/reverse?lat={lat}&lon={lon}').json()

    assert res['address']['village'] == 'Coaley'


def test_sunrise_sunset():
    lat, lon = 51.71640195, -2.3361588097703088
    sunrise, sunset = sunrise_sunset.get_monthly_sunrise_sunset(2023, lat, lon)
    assert len(sunrise) == 12

    s_sunrise = np.array(sunrise) 
    s_sunset = np.array(sunset) 
    s_day_length = s_sunset - s_sunrise

    assert s_day_length[0].seconds == 28320






