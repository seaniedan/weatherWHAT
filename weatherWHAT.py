#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# weather display
# by Sean Danischevsky 2019, 2022
#
# get weather from met office website
# https://www.metoffice.gov.uk/services/data/met-office-weather-datahub 
# and display on screen or Pimeroni InkyWhat
#
# this file takes the command line input and gets the forecast data
# then optionally calls
# weatherDisplay for display as an image on InkyWhat or as a saved image


import argparse        

try:
    import api
except:
    print ("Please register with The Meteorological Office, https://metoffice.apiconnect.ibmcloud.com/metoffice/production/ - enter your email adress and create a password, copy your API key and save it in a file next to this one, called\napi.py")
    raise Exception


def valid_date(s):
    # parse date inputs from user as string, output datetime object
    import datetime

    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "Please enter a date in the format 'YYYY-MM-DD'"
        raise argparse.ArgumentTypeError(msg)


def load_forecast(loadforecastfile):
    #load pickled forecast data

    import pickle

    return pickle.load(open(loadforecastfile, "rb"))


def save_forecast(forecast, now, local_timezone_name, local_now, saveforecast):
    #save forecast data as a pickle file
    #input a dir or filepath
    #return pickled then unpickled object

    import os
    import pickle

    if os.path.isdir(saveforecast):
        #create a filename      
        saveforecastfile= os.path.join(saveforecast, now.strftime("%Y_%m_%d__%H_%M") + '.pickle')
        print ('saved filename', saveforecastfile)
    else:
        saveforecastfile= saveforecast

    pickle.dump((forecast, now, local_timezone_name, local_now), open(saveforecastfile, "wb"))
    return pickle.load(open(saveforecastfile, "rb"))


#run on command line:
def display_weather(
    lat= api.lat, 
    lon= api.lon, 
    bg_file= None,
    bg_map= False, 
    zoom= False,
    show_on_inky= False, 
    inky_colour= None,
    show_image= False, 
    save_image= None,
    loadforecast= None,
    saveforecast= None,
    old= False,
    banner= '',
    location_banner='',
    verbose= False):

    # bg_file: image filepath for background. Can be a directory from which a random image is used.
    # bg_map: show location on map
    # zoom: show location on zoomed in map 
    # show_on_inky: display image on Pimeroni InkyWHAT
    # show_image: display image on screen
    # save_image: filepath to save resulting image
    # loadforecast: load forecast data from filepath instead of getting live forecast
    # saveforecast: filepath to save the forecast in a pickle file
    # old: if True, get historical wather forecast
    # banner: message to display
    # verbose: if True, display diagnostic info

    import met_weather

    #load or save pickled forecasts
    if loadforecast:
        forecast, now, local_timezone_name, local_now= load_forecast(loadforecast)  
        # TODO: need to set 'now' from forecast object
    else:
        # get current forecast
        now, local_timezone_name, local_now= met_weather.get_now(lon, lat)
        forecast= met_weather.get_forecast(lon, lat)

    if saveforecast:
        #save weather and reload it to check
        forecast, now, local_timezone_name, local_now= save_forecast(forecast, now, local_timezone_name, local_now, saveforecast)
    

    print (len(forecast))


    # Parse data for text display
    forecast_elements= {'local_now':local_now}

    # next sunrise and sunset times
    forecast_elements['sun_msg']= met_weather.get_next_sunrise_or_sunset_msg(now, api.lon, api.lat, local_timezone_name)


    features= forecast['features']
    timeSeries= features[0]['properties']['timeSeries']
    idx= met_weather.get_current_timestamp_index(forecast, now)

    # current temperature
    screenTemperature= timeSeries[idx]['screenTemperature']    
    forecast_elements['temperature_msg']= str(round(screenTemperature))+ "°"

    # high and low temperatures in the next 24 hours:
    forecast_elements['hi_lo_msg']= met_weather.get_high_low_msg(timeSeries[idx:][:24], now, local_timezone_name)

    #date
    forecast_elements["local_now"]= local_now.strftime("%A %d %b %Y")


    #short text forecast summary
    # TODO GET FROM RSS FEED
    summary= ""

    # get soonest alert
    #TODO: get alert from RSS feed
    alert= None

    #switch summary for alert if there is one
    if alert:
        summary= alert  

    forecast_elements["summary"]= summary

    forecast_elements["forecast_background"]= met_weather.significantWeatherCode[timeSeries[idx]['significantWeatherCode']]

    forecast_elements["hours"]= [met_weather.convert_utc_to_local(met_weather.convert_from_iso(t['time']), local_timezone_name).strftime("%H") for t in timeSeries[idx:][:24]]

    forecast_elements["uvIndex"]= [t['uvIndex'] for t in timeSeries[idx:][:24]]

    forecast_elements["precipitationRate"]= [t['precipitationRate'] for t in timeSeries[idx:][:24]]
    forecast_elements["probOfPrecipitation"]= [t['probOfPrecipitation']/100.0 for t in timeSeries[idx:][:24]]


    forecast_elements['temperatures']= [str(round(t['screenTemperature']))    for t in timeSeries[idx:][:24]]   



    #display weather in text only mode (not wrapped/formatted to screen).
    print ("#"*len(forecast_elements["hours"])*4)
    print (banner)
    print (location_banner)
    print (forecast_elements["local_now"]) #date
    print (forecast_elements["forecast_background"])
    print (forecast_elements["temperature_msg"])
    print (forecast_elements["hi_lo_msg"])
    print (forecast_elements["sun_msg"])
    print (forecast_elements["summary"])#'Overcast throughout the day.'   

    if verbose:
        print()
        print ("UV index:")
        print ("   ".join([str(hour) for hour in forecast_elements["uvIndex"]]))
        print()
        print ('Precipitation Rate:')
        print ("   ".join([str(hour) for hour in forecast_elements["precipitationRate"]]))
        print ('Precipitation intensity:')
        print (" ".join([str(hour) for hour in forecast_elements["probOfPrecipitation"]]))
        print ("Hourly Temperature")
        print ("  ".join(forecast_elements['temperatures']))
        print ("  ".join([hour for hour in forecast_elements["hours"]]))



    print ("#"*len(forecast_elements["hours"])*4)

    if save_image or show_image or show_on_inky:
        import weatherDisplay
        weatherDisplay.main(forecast_elements, 
        lat, lon, 
        bg_file, 
        bg_map, 
        zoom, 
        show_on_inky, 
        inky_colour, 
        show_image, 
        save_image, 
        banner, 
        location_banner, 
        verbose)


#run on command line:
if __name__ == "__main__":
    parser= argparse.ArgumentParser()

    #verbose
    parser.add_argument(
        '-v', '--verbose',
        help= 'show diagnostic info.',
        action= "store_true")

    #Banner
    parser.add_argument(
        '-b', '--banner',
        help= 'banner message at top of screen.',
        default= '',
        required= False)

    #mutually exclusive group: latlong or location
    location= parser.add_mutually_exclusive_group()

    #latitude, longitude
    location.add_argument(
        '-ll', '--latlong',
        type= (str),
        help= "forecast for location as 'latitude, longitude'. Use quotes and a space before negative numbers, e.g. -ll ' -5.55 66' .",
        required= False)

    #latitude, longitude
    location.add_argument(
        '-l', '--location',
        help= 'forecast for location in plain text, e.g. postode, streetname. Requires https://github.com/geopy/geopy ',
        required= False)

    # mutually exclusive group: map or zoomed map
    bg= parser.add_mutually_exclusive_group()
    #World Map Display
    bg.add_argument(
        '-m', '--map',
        help= 'Show world map with forecast location.',
        action= "store_true",
        required= False)

    # world map display
    bg.add_argument(
        '-z', '--zoom',
        help= 'Show zoomed world map with forecast location.',
        action= "store_true",
        required= False)

    #filepath of image to Display. If a folder, choose randomly from that folder. 
    bg.add_argument(
        '-bg', '--bg',
        help= 'Filepath of background image to display. If a folder, choose randomly from that folder. If the folders have one of the following values: clear-day, clear-night, rain, snow, sleet, wind, fog, cloudy, partly-cloudy-day, or partly-cloudy-night, the appropriate weather background will be taken from that folder.',
        default= None,
        required= False)

    #InkyWhat
    parser.add_argument(
        '-i', '--inky',
        help= 'Show image on the InkyWhat.',
        action= "store_true",
        required= False)

    parser.add_argument('--type', '-t', type=str, required=False, choices=["what", "phat"], default= "what", help="type of display")

    parser.add_argument('--colour', '-c', type=str, required=False, choices=["red", "black", "yellow"], default= "black", help="ePaper display colour")

    #Display Image
    parser.add_argument(
        '-d', '--display',
        help= 'Show image on the screen display.',
        action= "store_true",
        required= False)

    #Save Image
    parser.add_argument(
        '-s', '--save',
        help= 'Save image filepath.',
        required= False)

    #Save pickle of forecast  to this filepath
    parser.add_argument(
        '-sf', '--saveforecast',
        help= "save forecast data to filepath, e.g. '/path/weather.pickle'. If filepath is a directory, the filename will be automatically generated and place in that directory.",
        required= False)

    #mutually exclusive group: load pickle or ask for previous forecast data
    forecast_time= parser.add_mutually_exclusive_group()

    #Load Pickle instead of getting current forecast
    forecast_time.add_argument(
        '-lf', '--loadforecast',
        help= 'load forecast data from filepath instead of live forecast.',
        required= False)

    #get forecast for this date and time.
    forecast_time.add_argument(
        '-o', '--old',
        help= "get forecast for this date and time. Use 'YYYY-MM-DD'. You don't need to add hours and minutes.",
        type= valid_date,
        required= False)

    args= parser.parse_args()

    location_banner= ""

    if args.latlong:
        latlong= args.latlong
        lat, lon= latlong.split(',')
        if args.verbose: 
            print ('Latitude, Longitude from command arguments:', lat, ",", lon)
    elif args.location:
        from geopy.geocoders import Nominatim
        geolocator= Nominatim(user_agent= api.user_agent)      
        location= geolocator.geocode(args.location)
        try:
            if args.verbose: 
                print (location.raw)
            lat, lon= location.latitude, location.longitude
            location_banner= location.address
            if args.verbose: 
                print ('Latitude, Longitude from geopy:', lat, ",", lon)
        except AttributeError:
            print (f"Sorry, Geopy could not find location {args.location}!\nTry searching https://nominatim.openstreetmap.org/\nor look up the latitude and longitude on Google Maps, and enter the latitude and longitude with the '-ll' option.")
            exit()
    else:
        # use default location from secrets file
        lat= api.lat
        lon= api.lon
        if args.verbose: 
            print ('Latitude, Longitude from secrets file:', lat, ",", lon)
        # could be useful for map zoom:
        # add variables to zoom to optionally take a box
        # location.raw['boundingbox'] returns latitude min, max, longitude min, max:
        # ['48.8155755', '48.902156', '2.224122', '2.4697602']
        # print ("{}\nLatitude, Longitude:\n{}, {}".format(location.address, location.latitude, location.longitude))

    if (args.bg or args.map or args.zoom) and (not args.inky and not args.display and not args.save):
        # user has gone to the trouble of specifting an image, but they won't see it!
        parser.error("--bg, --map or --zoom requires --display, --save or --inky.")
    

    display_weather(
        lat= lat,
        lon= lon, 
        bg_file= args.bg,
        bg_map= args.map, 
        zoom= args.zoom,
        show_on_inky= args.inky, 
        inky_colour= args.colour,
        show_image= args.display, 
        save_image= args.save, 
        loadforecast= args.loadforecast,
        saveforecast= args.saveforecast,
        old= args.old,
        banner= args.banner,
        location_banner= location_banner,
        verbose= args.verbose)
