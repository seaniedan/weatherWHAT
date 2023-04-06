#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# get weather from Met Office
# by Sean Danischevsky
# install: I used:
# /usr/local/bin/python3 -m pip install geojson suncalc python-dateutil 
# /usr/local/bin/python3 -m pip install timezonefinder[numba] --user # also installs optional dependencies for increased performance

#later in venv I used venv:
# cd weatherWHAT
# python -m venv venv
# source venv/bin/activate
# pip install geojson suncalc python-dateutil timezonefinder geopy

# support: https://groups.google.com/g/metoffice-datapoint

import api
import datetime    
from dateutil import tz

def get_now(lon, lat):
    now= datetime.datetime.now().astimezone(datetime.timezone.utc)
    local_timezone_name= get_local_timezone_name(lon, lat)
    local_now= convert_utc_to_local(now, local_timezone_name)
    return now, local_timezone_name, local_now


def get_local_timezone_name(lon, lat):
    #given a longitude and latitude, return the local time name, e.g. 'Europe/Berlin'

    from timezonefinder import TimezoneFinder

    tf = TimezoneFinder()
    return tf.timezone_at(lng= lon, lat= lat)  # 'Europe/Berlin'




def convert_from_iso(date_string):
    # input time (date_string): 2022-08-01T17:00Z 
    # outputs timezone-aware datetime object, in UTC
    import datetime
    return datetime.datetime.fromisoformat(date_string[:-1]).astimezone(datetime.timezone.utc)



def convert_utc_to_local(datetime_object, local_timezone_name):
    # given a datetime object as UTC 
    # and a local timezone name, e.g. 'Europe/Berlin'
    # return local time

    from dateutil import tz

    to_zone = tz.gettz(local_timezone_name)
    #print (to_zone) # tzfile('/usr/share/zoneinfo/Europe/Berlin')
    return datetime_object.astimezone(to_zone)







def get_next_sunrise_or_sunset_msg(now, lon, lat, local_timezone_name):
    import suncalc
    import datetime

    try:

        suncalc_times= suncalc.get_times(now, lon, lat)
        sunrise= suncalc_times['sunrise']
        sunrise_utc= datetime.datetime.fromtimestamp(sunrise.replace(tzinfo=datetime.timezone.utc).timestamp(), tz=datetime.timezone.utc)
        sunset= suncalc_times['sunset']
        sunset_utc= datetime.datetime.fromtimestamp(sunset.replace(tzinfo=datetime.timezone.utc).timestamp(), tz=datetime.timezone.utc)

        if (sunrise_utc < now < sunset_utc):
            #it's day time            
            next_sunrise_or_sunset_msg= "sunset\n{}".format(convert_utc_to_local(sunset_utc, local_timezone_name).strftime("%H:%M"))

        else:
            # night time
            next_sunrise_or_sunset_msg= "sunrise\n{}".format(convert_utc_to_local(sunrise_utc, local_timezone_name).strftime("%H:%M"))
    except AttributeError:
        #We're at the North pole and there's no sunset
        next_sunrise_or_sunset_msg= ""


    return next_sunrise_or_sunset_msg



def get_forecast(lon, lat):

    import http.client
    import json

    #request
    conn = http.client.HTTPSConnection("api-metoffice.apiconnect.ibmcloud.com")

    headers = {
        'X-IBM-Client-Id': api.clientId,
        'X-IBM-Client-Secret': api.clientSecret,
        'accept': "application/json"
        }

    #conn.request("GET", f"/v0/forecasts/point/daily?excludeParameterMetadata=REPLACE_THIS_VALUE&includeLocationName=REPLACE_THIS_VALUE&latitude={lat}&longitude={lon}", headers=headers)
    conn.request("GET", f"/v0/forecasts/point/hourly?excludeParameterMetadata=REPLACE_THIS_VALUE&includeLocationName=true&latitude={lat}&longitude={lon}", headers=headers)
    res = conn.getresponse()
    data = res.read()

    #print(data.decode("utf-8"))
    ##################
    #decode json


    return json.loads(data)



def get_daily_forecast(lon, lat):

    import http.client
    import json
    
    #parameters
    #print (lon)
    #print (lat)

    #request
    conn = http.client.HTTPSConnection("api-metoffice.apiconnect.ibmcloud.com")

    headers = {
        'X-IBM-Client-Id': api.clientId,
        'X-IBM-Client-Secret': api.clientSecret,
        'accept': "application/json"
        }

    conn.request("GET", f"/v0/forecasts/point/daily?excludeParameterMetadata=REPLACE_THIS_VALUE&includeLocationName=REPLACE_THIS_VALUE&latitude={lat}&longitude={lon}", headers=headers)
    #conn.request("GET", f"/v0/forecasts/point/hourly?excludeParameterMetadata=REPLACE_THIS_VALUE&includeLocationName=true&latitude={lat}&longitude={lon}", headers=headers)
    res = conn.getresponse()
    data = res.read()

    #print(data.decode("utf-8"))
    ##################
    #decode json


    return json.loads(data)



# met office api significant weather codes
significantWeatherCode= {0: "Clear night",
1: "Sunny day",
2: "Partly cloudy (night)",
3: "Partly cloudy (day)",
4: "Not used",
5: "Mist",
6: "Fog",
7: "Cloudy",
8: "Overcast",
9: "Light rain shower (night)",
10: "Light rain shower (day)",
11: "Drizzle",
12: "Light rain",
13: "Heavy rain shower (night)",
14: "Heavy rain shower (day)",
15: "Heavy rain",
16: "Sleet shower (night)",
17: "Sleet shower (day)",
18: "Sleet",
19: "Hail shower (night)",
20: "Hail shower (day)",
21: "Hail",
22: "Light snow shower (night)",
23: "Light snow shower (day)",
24: "Light snow",
25: "Heavy snow shower (night)",
26: "Heavy snow shower (day)",
27: "Heavy snow",
28: "Thunder shower (night)",
29: "Thunder shower (day)",
30: "Thunder"}





def get_current_timestamp_index(forecast, given_time):
    # parse met office JSON file to get nearest timestamp to given_time

    features = forecast['features']
    timeSeries= features[0]['properties']['timeSeries']
    # return min(timeSeries, key=lambda x:abs(convert_from_iso(x['time'])- given_time))
    idx= min(range(len(timeSeries)), key= lambda x: abs(convert_from_iso(timeSeries[x]['time'])- given_time))
    idx= min(range(len(timeSeries)), key= lambda t: abs(
        datetime.datetime.fromisoformat(timeSeries[t]['time'][:-1]).replace(tzinfo= datetime.timezone.utc)
        - given_time))
    return idx



def get_high_low_msg(timeSeries, now, local_timezone_name):
    #parse met office JSON file to get highest temperature in next 24 hours

    high= max(timeSeries, key= lambda time: time['screenTemperature'])
    low= min(timeSeries, key= lambda time: time['screenTemperature'])

    # choose hi/lo: earliest low, unless it's less than an hour away.
    low_time_utc= datetime.datetime.fromtimestamp(convert_from_iso(low['time']).replace(tzinfo= datetime.timezone.utc).timestamp(), tz= datetime.timezone.utc)

    high_time_utc= datetime.datetime.fromtimestamp(convert_from_iso(high['time']).replace(tzinfo= datetime.timezone.utc).timestamp(), tz= datetime.timezone.utc)

    if (low_time_utc < high_time_utc) and (convert_from_iso(low['time']) > now):
        # low is next
        high_low_msg= "low {}°\n{}".format(str(round(low['screenTemperature'])), convert_utc_to_local(convert_from_iso(low['time']), local_timezone_name).strftime("%H:%M"))
    else:
        # high is next 
        high_low_msg= "high {}°\n{}".format(str(round(high['screenTemperature'])), convert_utc_to_local(convert_from_iso(high['time']), local_timezone_name).strftime("%H:%M")) 

    return high_low_msg



def make_default_icon_dirs():
    import os
    for forecast_icon in significantWeatherCode.values():
        #print (icon)
        #print (os.path.join(, icon))
        basedir= os.path.join(os.path.dirname(__file__), 'icons','default', forecast_icon)
        #print (basedir)
        os.mkdir(basedir)


if __name__=="__main__":
    #make_default_icon_dirs()
    #exit()
    now, local_timezone_name, local_now= get_now(api.lon, api.lat)
    print ("Time now:", now)
    print (f"Now as {local_timezone_name}: {local_now}")

    # sunrise/sunset time
    print (get_next_sunrise_or_sunset_msg(now, api.lon, api.lat, local_timezone_name))

    # hourly forecast
    forecast= get_forecast(api.lon, api.lat)
    #print (forecast)

    #daily= get_daily_forecast(lon, lat)
    #print (daily)

    features= forecast['features']
    timeSeries= features[0]['properties']['timeSeries']
    idx= get_current_timestamp_index(forecast, now)



    # current temperature
    screenTemperature= timeSeries[idx]['screenTemperature']    
    temperature_msg= str(round(screenTemperature))+ "°"

    print ("temperature:")
    print(temperature_msg)


    # significant weather code, e.g. 'Light rain shower (night)'
    print(significantWeatherCode[timeSeries[idx]['significantWeatherCode']])


    # hi / low temperature
    print (get_high_low_msg(timeSeries[idx:][:24], now, local_timezone_name))
    
    # summary_message,
    # replace with forecast symbols for next days    
    # of there's an alert, replace with alert:
    # https://www.metoffice.gov.uk/weather/guides/rss

    # times (hours for rain, UV, etc)
    hours=[convert_utc_to_local(convert_from_iso(t['time']), local_timezone_name).strftime("%H") for t in timeSeries[idx:][:24]]
    print (hours)

    # UV index
    uvIndex= [t['uvIndex'] for t in timeSeries[idx:][:24]]
    print ("uvIndex:")
    print(uvIndex)

    # Rain forecast
    precipitationRate= [t['precipitationRate'] for t in timeSeries[idx:][:24]]
    print ("precipitationRate:")
    print(precipitationRate)
    probOfPrecipitation= [t['probOfPrecipitation']/100.0 for t in timeSeries[idx:][:24]]
    print ("probOfPrecipitation:")
    print(probOfPrecipitation)