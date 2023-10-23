
import calendar
import csv
import numpy as np
import pandas as pd
import datetime as datetime
from dateutil import parser
from pandas.plotting import register_matplotlib_converters
import matplotlib as plt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

Day_Length_Fraction = 1.0
Solar_Panel_Base_Size = 40.0
Daytime_Price=0.361
Nighttime_Price=0.266
Standing_Charge=0.453

# Define Current System
Solar_panel = 40.0
Battery = 44.2
Battery_Fudge1 = 5.0
Battery_Fudge2 = 1.0

months = ['January', ' February', ' March', 'April', 'May', 'June',
          'July', 'August', 'September', 'October', 'November', 'December']

# how many days in each month
daysinmonth = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])

sun_rise = np.array([datetime.timedelta(hours=7, minutes=57),datetime.timedelta(hours=7, minutes=12),
                     datetime.timedelta(hours=6, minutes=13), datetime.timedelta(hours=6, minutes=3),
                     datetime.timedelta(hours=5, minutes=6), datetime.timedelta(hours=4, minutes=40),
                     datetime.timedelta(hours=4, minutes=58), datetime.timedelta(hours=5, minutes=44),
                     datetime.timedelta(hours=6, minutes=33), datetime.timedelta(hours=7, minutes=22),
                     datetime.timedelta(hours=7, minutes=16), datetime.timedelta(hours=7, minutes=57)
                     ]) 
sun_set = np.array([datetime.timedelta(hours=16, minutes=22),datetime.timedelta(hours=17, minutes=16),
                    datetime.timedelta(hours=18, minutes=5), datetime.timedelta(hours=19, minutes=58),
                    datetime.timedelta(hours=20, minutes=47), datetime.timedelta(hours=21, minutes=21), 
                    datetime.timedelta(hours=21, minutes=14), datetime.timedelta(hours=20, minutes=26), 
                    datetime.timedelta(hours=19, minutes=18), datetime.timedelta(hours=18, minutes=10), 
                    datetime.timedelta(hours=16, minutes=13), datetime.timedelta(hours=15, minutes=53)
                    ]) 

Night_time_start = datetime.timedelta (hours=24, minutes=0)
Night_time_end = datetime.timedelta (hours=31, minutes = 0)

day_length = np.subtract ( sun_set , sun_rise)
daylight_hours = day_length / datetime.timedelta(hours=1)
#daylight_hours = daylight_sec / 3600

evening_hours = Night_time_start-sun_set
evening_hours = evening_hours / datetime.timedelta (hours=1)
#evening_hours = evening_hours / 3600

monthly_consumption = np.array([2098,2048,2035,1731,1542,1465,1419,1390,1528,1705,1945,2095])
consumption_multiplier = 1.0

monthly_consumption = np.multiply(consumption_multiplier,monthly_consumption)
daily_consumption = np.divide (monthly_consumption,daysinmonth)
hourly_consumption = np.divide(daily_consumption,24)

monthly_Generation = np.array ([1266,1800,3034,3979,4892,5054,5071,4438,3330,2329,1391,1054])
monthly_Generation = monthly_Generation * Solar_panel / Solar_Panel_Base_Size

Daily_Generation = monthly_Generation / daysinmonth
Hourly_Generation = Daily_Generation/daylight_hours

Production_Difference = (Daily_Generation - daily_consumption)/(daylight_hours)

#calculate the amount of electricity used while the sun is shining
Daily_day_time_usage_sun=hourly_consumption*daylight_hours
#calculate any surplus electricity generated that can go into the battery
surplus_daytime_generation=Daily_Generation-Daily_day_time_usage_sun
surplus_daytime_generation [surplus_daytime_generation< 0]=0

#Can we charge the battery overnight on cheap night time electriciy.  We only want to do this if its likely
#the sun wont be shining enough to satisfy the whole days usage.  Ive used a fairly course fudge here.
Battery_overnight_charge = np.zeros (12)
Battery_overnight_charge [surplus_daytime_generation< Battery_Fudge1] = Battery_Fudge2

#What is the battery level at the start of the day - ie has it been charged overnight or is there some left 
#from yesterdays charging.
Battery_Status_1=Battery*Battery_overnight_charge

#Now calculate how much electricity we need to import because the battery isnt big enough and the suns not shining enough
Electricity_import = Daily_Generation - Daily_day_time_usage_sun
Electricity_import [Electricity_import > 0] = 0
Electricity_import = abs(Electricity_import)
Electricity_import [Electricity_import - Battery_Status_1 < 0 ] = 0


#Now Calculate how we much we are exporting
Electricity_Export= Battery_Status_1 + Daily_Generation - Daily_day_time_usage_sun - Battery
Electricity_Export [Electricity_Export <0] = 0

#Whats the battery status at the end of daylight
Battery_Status_2 = Battery_Status_1 + Daily_Generation - Daily_day_time_usage_sun
Battery_Status_2 [Battery_Status_2 <0] = 0
Battery_Status_2 [Battery_Status_2 > Battery] = Battery

#Whats the evening consumption after the sun has set up to the cheap electricity time
Evening_consumption = evening_hours*hourly_consumption
Evening_use_daytime_price = Battery_Status_2 - Evening_consumption
Evening_use_daytime_price [Evening_use_daytime_price > 0] = 0
Evening_use_daytime_price = abs(Evening_use_daytime_price)

#whats the staus of the battery at the end of the evening
Battery_status_3 = Battery_Status_2 - Evening_consumption
Battery_status_3 [Battery_status_3 <0] = 0

#consumption of night time electricity
#How Long is Night time electricity
Night_hours = Night_time_end - Night_time_start
Night_hours = Night_hours / datetime.timedelta (hours=1)
Night_consumption = Night_hours*hourly_consumption-Battery_status_3
Night_consumption [Night_consumption < 0] = 0

#whats the battery status at the end of night time electricity
Battery_status_4 =  Battery_status_3 - Night_hours*hourly_consumption
Battery_status_4 [Battery_status_4 < 0] = 0

#How much electricity do we use to recharge the battery 
Battery_consumption = Battery_overnight_charge * Battery - Battery_status_4
Battery_consumption [Battery_consumption <0] = 0

# Total Up the Consumption
Total_Day_Consumption = Evening_use_daytime_price + Electricity_import
Total_Night_Consumption = Night_consumption + Battery_consumption

#Total Consumption
Total_consumption = Total_Day_Consumption+Total_Night_Consumption

for ip in range(12):
    print(months[ip],Total_Day_Consumption[ip],Total_Night_Consumption[ip], Total_consumption[ip])
