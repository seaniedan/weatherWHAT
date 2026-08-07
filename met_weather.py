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
import ss_download
    # from https://raw.githubusercontent.com/MetOffice/weather_datahub_utilities/main/site_specific_download/ss_download.py
    # i replaced print(req.text)
    # with return (req.json())
import datetime
from dateutil import tz

import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)


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
    # input time (date_string): 2022-08-01T17:00Z (the trailing Z means UTC)
    # outputs timezone-aware datetime object, in UTC
    # NOTE: use replace(), not astimezone(): the parsed value is naive, and
    # astimezone() would assume it's in the *runner's* local timezone, shifting
    # every hour label/time by the machine's UTC offset (e.g. -7h on a PDT host).
    import datetime
    return datetime.datetime.fromisoformat(date_string[:-1]).replace(tzinfo=datetime.timezone.utc)



def convert_utc_to_local(datetime_object, local_timezone_name):
    # given a datetime object as UTC
    # and a local timezone name, e.g. 'Europe/Berlin'
    # return local time

    from dateutil import tz

    to_zone = tz.gettz(local_timezone_name)
    #print (to_zone) # tzfile('/usr/share/zoneinfo/Europe/Berlin')
    return datetime_object.astimezone(to_zone)







def _next_sun_event(now, lon, lat):
    # Which solar event is next from `now`: returns ('sunrise'|'sunset', event_utc)
    # or (None, None) at the poles where there may be no sunrise/sunset.
    import suncalc
    import datetime

    try:
        suncalc_times= suncalc.get_times(now, lon, lat)
        sunrise= suncalc_times['sunrise']
        sunrise_utc= datetime.datetime.fromtimestamp(sunrise.replace(tzinfo=datetime.timezone.utc).timestamp(), tz=datetime.timezone.utc)
        sunset= suncalc_times['sunset']
        sunset_utc= datetime.datetime.fromtimestamp(sunset.replace(tzinfo=datetime.timezone.utc).timestamp(), tz=datetime.timezone.utc)
    except AttributeError:
        #We're at the North pole and there's no sunset
        return None, None

    if (sunrise_utc < now < sunset_utc):
        return "sunset", sunset_utc      # it's day time; sunset is next
    else:
        return "sunrise", sunrise_utc    # night time; sunrise is next


def get_next_sunrise_or_sunset_msg(now, lon, lat, local_timezone_name):
    # Text form, e.g. "sunset\n21:13". The "sunrise"/"sunset" literals are what
    # the Coesfeld ansible patch rewrites to arrows, so keep them verbatim.
    event, event_utc= _next_sun_event(now, lon, lat)
    if event is None:
        return ""
    return "{}\n{}".format(event, convert_utc_to_local(event_utc, local_timezone_name).strftime("%H:%M"))


def moon_phase_icon(dt):
    # Meteocons icon name for the moon phase at `dt` (a tz-aware datetime).
    # Dependency-free synodic-month calc (this suncalc build has no moon support),
    # referenced to a known new moon (2000-01-06 18:14 UTC).
    import datetime
    icons= ("moon-new-fill", "moon-waxing-crescent-fill", "moon-first-quarter-fill", "moon-waxing-gibbous-fill",
            "moon-full-fill", "moon-waning-gibbous-fill", "moon-last-quarter-fill", "moon-waning-crescent-fill")
    ref= datetime.datetime(2000, 1, 6, 18, 14, tzinfo=datetime.timezone.utc)
    synodic_month= 29.530588853
    frac= (((dt- ref).total_seconds()/ 86400.0) % synodic_month)/ synodic_month
    return icons[int(frac* 8+ 0.5) % 8]


def get_sun_indicator(now, lon, lat, local_timezone_name):
    # Structured form for the icon display mode: the next solar event's time plus
    # the Meteocons icon to show for it — the sun for a coming sunrise, the
    # current moon phase for a coming sunset. Returns None at the poles.
    event, event_utc= _next_sun_event(now, lon, lat)
    if event is None:
        return None
    return {
        "event": event,
        "time": convert_utc_to_local(event_utc, local_timezone_name).strftime("%H:%M"),
        "icon": "clear-day-fill" if event == "sunrise" else moon_phase_icon(now),
    }





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



def _next_temp_extreme(timeSeries, now, local_timezone_name):
    # Which temperature extreme to show next: returns (event, temp_rounded, time_str)
    # where event is 'high' or 'low'. Earliest low, unless it isn't still ahead.
    high= max(timeSeries, key= lambda time: time['screenTemperature'])
    low= min(timeSeries, key= lambda time: time['screenTemperature'])

    low_time_utc= datetime.datetime.fromtimestamp(convert_from_iso(low['time']).replace(tzinfo= datetime.timezone.utc).timestamp(), tz= datetime.timezone.utc)
    high_time_utc= datetime.datetime.fromtimestamp(convert_from_iso(high['time']).replace(tzinfo= datetime.timezone.utc).timestamp(), tz= datetime.timezone.utc)

    if (low_time_utc < high_time_utc) and (convert_from_iso(low['time']) > now):
        pick= low
        event= "low"
    else:
        pick= high
        event= "high"
    time_str= convert_utc_to_local(convert_from_iso(pick['time']), local_timezone_name).strftime("%H:%M")
    return event, round(pick['screenTemperature']), time_str


def get_high_low_msg(timeSeries, now, local_timezone_name):
    #parse met office JSON file to get highest temperature in next 24 hours
    event, temp, time_str= _next_temp_extreme(timeSeries, now, local_timezone_name)
    # keep the "low "/"high " literals verbatim — the Coesfeld ansible patch
    # rewrites them to min/max.
    if event == "low":
        return "low {}°\n{}".format(str(temp), time_str)
    else:
        return "high {}°\n{}".format(str(temp), time_str)


def get_temp_indicator(timeSeries, now, local_timezone_name):
    # Structured form for icon mode: the next temperature extreme. `event`
    # ('high'/'low') selects the ▲/▼ triangle drawn alongside the temperature.
    event, temp, time_str= _next_temp_extreme(timeSeries, now, local_timezone_name)
    return {
        "event": event,
        "temp": str(temp) + "°",
        "time": time_str,
    }



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
    forecast = ss_download.retrieve_forecast(ss_download.base_url, "hourly", {"apikey": api.key}, api.lat, api.lon, "FALSE", "TRUE")
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
