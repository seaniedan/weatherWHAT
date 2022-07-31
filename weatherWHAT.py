#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# weather display
# by Sean Danischevsky 2019
#
# get weather from Darksky and display on screen or Pimeroni InkyWhat
# this file takes the command line input and passes the forecast data
# to weatherDisplay for processing and display


#default preferences
latlong= (51.5515, -0.1344) # default location for weather forecast. Get this by copying from Google Maps URL.

#imports
import argparse        



def valid_date(s):
    # parse date inputs from user as string, output datetime object
    import datetime

    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "Please enter a date in the format 'YYYY-MM-DD'"
        raise argparse.ArgumentTypeError(msg)





def read_lines(filename):
    #output a text file as a list of lines
    with open(filename) as f:
        content = f.readlines()
        #remove whitespace characters like `\n` at the end of each line
        content = [x.strip() for x in content] 
    return content

def read_line(filename):
    #output a text file andread first line
    with open(filename) as f:
        line = f.readline().strip()
    return line

def get_API_from_file():
    import os

    try:
        api_path= os.path.join(os.path.dirname(__file__), 'api.txt')
        API_KEY= read_line(api_path)
        return API_KEY
    except:
        print ("Please register with The Meteorological Office, https://metoffice.apiconnect.ibmcloud.com/metoffice/production/ - enter your email adress and create a password, copy your API key and save it in a file next to this one, called\napi.txt")
        raise Exception






def load_forecast(loadforecastfile):
    #load pickled forecast data

    import pickle

    return pickle.load(open(loadforecastfile, "rb"))




def save_forecast(forecast, saveforecast):
    #save forecast data as a pickle file
    #input a dir or filepath
    #return pickled then unpickled object

    import os
    import datetime
    import pickle

    if os.path.isdir(saveforecast):
        #create a filename
        now= datetime.datetime.now()
        now= now.strftime("%Y_%m_%d__%H_%M")        
        saveforecastfile= os.path.join(saveforecast, now+ '.pickle')
        print ('saved filename', saveforecastfile)
    else:
        saveforecastfile= saveforecast

    pickle.dump(forecast, open(saveforecastfile, "wb"))
    return pickle.load(open(saveforecastfile, "rb"))






#run on command line:
def display_weather(
    latlong= latlong, 
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
    import datetime

    #load or save pickled forecasts
    if loadforecast:
        forecast= load_forecast(loadforecast)  
    elif old:
        # datetime(year, month, day, hour, minute, second, microsecond)
        forecast= get_old_weather(latlong, old) #old must be a datetime object
    else:
        forecast= met_weather.get_forecast(latlong)



    if saveforecast:
        #save weather and reload it to check
        forecast= save_forecast(forecast, saveforecast)
    


    # Parse data for text display
    # high and low temperatures in the next 24 hours:

    # data[0] = today, but I don't use
    # temperature_high_time= forecast.daily.data[0].temperature_high_time
    # because high for the next day would appear after midnight
    # and I wanted to see the low at 7am (or whenever it was still coming)
    high= met_weather.high(forecast)
    low= min(forecast.hourly.data[:24], key= lambda x: x.temperature)

    #short text forecast summary
    summary= forecast.hourly.summary

    # next sunrise and sunset times
    sunrise_time= forecast.daily.data[0].sunrise_time
    sunset_time= forecast.daily.data[0].sunset_time

    # get soonest alert
    alerts= forecast.alerts
    if alerts:
        min_alert= min(alerts, key= lambda x: x.time)
        alert= "{}: {}".format(min_alert.time.strftime("%A %H:%M"), min_alert.title)
        #alerts+= "\n".join(alert for alert in set(forecast_alert_titles))
    else:
        alert= None










    #choose and format data for text
    temperature_msg= str(round(forecast.currently.temperature))+ "°"
    update_msg= "\n".join((banner, location_banner, forecast.currently.time.strftime("%A %d %b %Y")))


    #hi/lo 
    if (low.time < high.time) and low.time- forecast.currently.time > datetime.timedelta(hours= 1):# and (low.time- forecast.currently.time).seconds > datetime.timedelta(hours= 1).seconds: 
        high_next= False 
        hi_lo_msg= "low({}) @ {}".format(str(round(low.temperature))+ "°", low.time.strftime("%H:%M"))       

    else:
        #high time is next 
        high_next= True
        hi_lo_msg= "high({}) @ {}".format(str(round(high.temperature))+ "°", high.time.strftime("%H:%M"))  



    #sunrise/sunset time
    try:
        if (sunrise_time < forecast.currently.time < sunset_time):
            #it's day time
            sun_msg= "sunset @ {}".format(sunset_time.strftime("%H:%M"))
            summary= forecast.hourly.summary.rstrip(".")
        else:
            # night time
            sun_msg= "sunrise @ {}".format(sunrise_time.strftime("%H:%M"))
            summary= forecast.daily.summary.rstrip(".")
    except:
        #We're at the North pole and there's no sunset
        sun_msg= ""
        summary= forecast.hourly.summary.rstrip(".")





    #switch summary for alert if there is one
    if alert:
        summary= alert  


    #here is where you could do a check to see if the screen needs updating-
    #save old version and if new != old, update







    if verbose:
        print()
        print ("TEMPERATURE")
        for hour in forecast.hourly.data:
            print (hour.time.strftime("%A %d %b %Y %H:%M"), hour.temperature)     
        print()
        print ("CLOUD COVER")
        for hour in forecast.hourly.data:
            print (hour.time.strftime("%A %d %b %Y %H:%M"), hour.cloud_cover)                      
        print()
        print ("UV INDEX")
        for hour in forecast.hourly.data:
            print (hour.time.strftime("%A %d %b %Y %H:%M"), hour.uv_index)  
        print()
        print ('forecast.currently.time:{}'.format(forecast.currently.time.strftime("%A %d %b %Y %H:%M")))
        print ("icon:", forecast.currently.icon)#'rain'
        print ("hourly summary:", forecast.hourly.summary)#'Overcast throughout the day.'
        print ("daily summary:", forecast.daily.summary)#'Light rain on Monday through next Saturday, with high temperatures falling to 22°C on Wednesday.'
        print ("current temperature:", forecast.currently.temperature), "degrees"#17.11
        print ('High:{}({})'.format(high.temperature, high.time.strftime("%A %d %b %Y %H:%M")))
        print ('Low:{}({})'.format(low.temperature, low.time.strftime("%A %d %b %Y %H:%M")))
        print ('current precipitation probability:', forecast.currently.precip_probability)
        print ('current precipitation intensity:', forecast.currently.precip_intensity)
        print ("sunrise time:", sunrise_time.strftime("%A %d %b %Y %H:%M")) 
        print ("sunset time:", sunset_time.strftime("%A %d %b %Y %H:%M"))     
        for alert in alerts:
            print("ALERT! {}: {}".format(alert.time.strftime("%A %H:%M"), alert.title))






    #display weather in text only mode (not wrapped/formatted to screen).
    print ("############################################")
    print (update_msg) #date
    print (forecast.currently.icon)
    print (temperature_msg)
    print (hi_lo_msg)
    print (sun_msg)
    print (summary)#'Overcast throughout the day.'       
    print ("############################################")




    if save_image or show_image or show_on_inky:
        import weatherDisplay
        weatherDisplay.main(forecast, 
        latlong, 
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
        #default= (51.5515, -0.1344)
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
        help= 'Filepath of background image to display. If a folder, choose randomly from that folder. If the folders have one of the following values: clear-day, clear-night, rain, snow, sleet, wind, fog, cloudy, partly-cloudy-day, or partly-cloudy-night, the appropriate weather icon will be taken from that folder.',
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
        if args.verbose: 
            print ('Latitude, Longitude:', latlong)
        latlong= latlong.split(',')
        latlong= [float(l) for l in latlong]

    elif args.location:
        from geopy.geocoders import Nominatim
        geolocator= Nominatim(user_agent= "Sean Danischevsky")
        location= geolocator.geocode(args.location)
        latlong= (location.latitude, location.longitude)
        #print (location.raw)
        # location.raw['boundingbox'] returns latitude min, max, longitude min, max:
        # ['48.8155755', '48.902156', '2.224122', '2.4697602']
        print ("{}\nLatitude, Longitude:\n{}, {}".format(location.address,location.latitude,location.longitude))
        location_banner= location.address

    if (args.bg or args.map or args.zoom) and (not args.inky and not args.display and not args.save):
        #user has gone to the trouble of specifting an image, but they won't see it!
        parser.error("--bg, --map or --zoom requires --display, --save or --inky.")
    

    display_weather(
        latlong= latlong, 
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


