import numpy as np
import pandas as pd
import datetime as datetime
import calendar
from . import sunrise_sunset

# Define electricty rate
daytime_price=0.361
nighttime_price=0.266
stanging_charge=0.453

# Define Current System
solar_panel_base_size = 40.0
solar_panel = 40.0
battery = 44.2
battery_fudge1 = 5.0
battery_fudge2 = 1.0

# how many days in each month
current_year = datetime.datetime.today().year
days_in_month =  [calendar.monthrange(current_year, month)[1] for  month in range(1,13)]

# https://api.sunrisesunset.io/json?lat=38.907192&lng=-77.036873&timezone=UTC

# sun_rise = np.array([datetime.timedelta(hours=7, minutes=57),datetime.timedelta(hours=7, minutes=12),
#                      datetime.timedelta(hours=6, minutes=13), datetime.timedelta(hours=6, minutes=3),
#                      datetime.timedelta(hours=5, minutes=6), datetime.timedelta(hours=4, minutes=40),
#                      datetime.timedelta(hours=4, minutes=58), datetime.timedelta(hours=5, minutes=44),
#                      datetime.timedelta(hours=6, minutes=33), datetime.timedelta(hours=7, minutes=22),
#                      datetime.timedelta(hours=7, minutes=16), datetime.timedelta(hours=7, minutes=57)
#                      ]) 
# sun_set = np.array([datetime.timedelta(hours=16, minutes=22),datetime.timedelta(hours=17, minutes=16),
#                     datetime.timedelta(hours=18, minutes=5), datetime.timedelta(hours=19, minutes=58),
#                     datetime.timedelta(hours=20, minutes=47), datetime.timedelta(hours=21, minutes=21), 
#                     datetime.timedelta(hours=21, minutes=14), datetime.timedelta(hours=20, minutes=26), 
#                     datetime.timedelta(hours=19, minutes=18), datetime.timedelta(hours=18, minutes=10), 
#                     datetime.timedelta(hours=16, minutes=13), datetime.timedelta(hours=15, minutes=53)
#                     ]) 
def run_solar_scheme():
    lat, lon = sunrise_sunset.get_lat_lon_from_address(
        city='Coaley',
        county='Gloucestershire',
        state='England',
        country='UK')
    sunrise, sunset = sunrise_sunset.get_monthly_sunrise_sunset(
        current_year,
        lat,
        lon)
    sunrise = np.array(sunrise)
    sunset = np.array(sunset)

    night_time_start = datetime.timedelta (hours=24, minutes=0)
    night_time_end = datetime.timedelta (hours=31, minutes = 0)

    day_length = np.subtract ( sunset , sunrise)
    daylight_hours = day_length / datetime.timedelta(hours=1)
    #daylight_hours = daylight_sec / 3600

    evening_hours = night_time_start-sunset
    evening_hours = evening_hours / datetime.timedelta (hours=1)
    #evening_hours = evening_hours / 3600

    monthly_consumption = np.array([2098,2048,2035,1731,1542,1465,1419,1390,1528,1705,1945,2095])
    consumption_multiplier = 1.0

    monthly_consumption = np.multiply(consumption_multiplier,monthly_consumption)
    daily_consumption = np.divide (monthly_consumption,days_in_month)
    hourly_consumption = np.divide(daily_consumption,24)  # TODO is assuming consumption is the same every hour good enough? Maycbe can guesstimate a 24 point array of relative usage.

    monthly_generation = np.array ([1266,1800,3034,3979,4892,5054,5071,4438,3330,2329,1391,1054])
    monthly_generation = monthly_generation * solar_panel / solar_panel_base_size

    daily_generation = monthly_generation / days_in_month
    hourly_generation = daily_generation/daylight_hours

    production_difference = (daily_generation - daily_consumption)/(daylight_hours)

    #calculate the amount of electricity used while the sun is shining
    daily_day_time_usage_sun=hourly_consumption*daylight_hours
    #calculate any surplus electricity generated that can go into the battery
    surplus_daytime_generation=daily_generation-daily_day_time_usage_sun
    surplus_daytime_generation [surplus_daytime_generation< 0]=0

    #Can we charge the battery overnight on cheap night time electriciy.  We only want to do this if its likely
    #the sun wont be shining enough to satisfy the whole days usage.  Ive used a fairly course fudge here.
    battery_overnight_charge = np.zeros (12)
    battery_overnight_charge [surplus_daytime_generation < battery_fudge1] = battery_fudge2

    #What is the battery level at the start of the day - ie has it been charged overnight or is there some left 
    #from yesterdays charging.
    battery_status_start_of_day=battery*battery_overnight_charge

    #Now calculate how much electricity we need to import because the battery isnt big enough and the suns not shining enough
    electricity_imported = daily_generation - daily_day_time_usage_sun
    electricity_imported [electricity_imported > 0] = 0
    electricity_imported = abs(electricity_imported)
    electricity_imported [electricity_imported - battery_status_start_of_day < 0 ] = 0

    #Now Calculate how we much we are exporting
    electricity_exported= battery_status_start_of_day + daily_generation - daily_day_time_usage_sun - battery
    electricity_exported [electricity_exported <0] = 0

    #Whats the battery status at the end of daylight
    battery_status_end_of_day = battery_status_start_of_day + daily_generation - daily_day_time_usage_sun
    battery_status_end_of_day [battery_status_end_of_day <0] = 0
    battery_status_end_of_day [battery_status_end_of_day > battery] = battery

    #Whats the evening consumption after the sun has set up to the cheap electricity time
    evening_consumption = evening_hours*hourly_consumption
    evening_use_daytime_price = battery_status_end_of_day - evening_consumption
    evening_use_daytime_price [evening_use_daytime_price > 0] = 0
    evening_use_daytime_price = abs(evening_use_daytime_price)

    #whats the staus of the battery at the end of the evening
    battery_status_end_of_evening = battery_status_end_of_day - evening_consumption
    battery_status_end_of_evening [battery_status_end_of_evening <0] = 0

    #consumption of night time electricity
    #How Long is Night time electricity
    night_hours = night_time_end - night_time_start
    night_hours = night_hours / datetime.timedelta (hours=1)
    night_consumption = night_hours*hourly_consumption-battery_status_end_of_evening
    night_consumption [night_consumption < 0] = 0

    #whats the battery status at the end of night time electricity
    battery_status_end_of_night =  battery_status_end_of_evening - night_hours*hourly_consumption
    battery_status_end_of_night [battery_status_end_of_night < 0] = 0

    #How much electricity do we use to recharge the battery 
    battery_consumption = battery_overnight_charge * battery - battery_status_end_of_night
    battery_consumption [battery_consumption <0] = 0

    # Total Up the Consumption
    total_day_consumption = evening_use_daytime_price + electricity_imported
    total_night_consumption = night_consumption + battery_consumption

    #Total Consumption
    total_consumption = total_day_consumption+total_night_consumption

    #Combine the results into a pandas dataframe
    df_result = pd.DataFrame(
        index=[calendar.month_name[i] for i in range(1,13)],
        data={
            'total_day_consumption': total_day_consumption,
            'total_night_consumption': total_night_consumption,
            'total_consumption': total_consumption,
        })

    return df_result
