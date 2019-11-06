#!/usr/bin/env python3

#make sequence of images
#input a dir containing pickled forecasts from weatherWHAT.py

# to convert sequence into a gif: 
# convert -delay 0 //Ixxx_v001.*.png -resize 960x540\ -loop 0 movie.gif


#imports
import argparse
import os
import weatherWHAT




#run on command line:
if __name__ == "__main__":
    parser = argparse.ArgumentParser()



    #verbose
    parser.add_argument(
        '-v', '--verbose',
        help= 'show diagnostic info. Not yet implemented.',
        action= "store_true")

    #csv
    parser.add_argument(
        '-c', '--csv',
        help= 'location to save the result as a .csv file. e.g. /mnt/projects/00temp/weather.csv ...not yet implemented',
        required= False)



    #mutually exclusive group: latlong or location
    location= parser.add_mutually_exclusive_group()



    #latitude, longitude
    location.add_argument(
        '-ll', '--latlong',
        type= (str),
        help= "forecast for location in as ' latitude, longitude'. Use quotes and a space before negative numbers",
        required= False)


    #latitude, longitude
    location.add_argument(
        '-l', '--location',
        help= 'forecast for location in plain text, e.g. postode, streetname. Requires https://github.com/geopy/geopy ',
        #default= (51.5515, -0.1344)
        required= False)





    #mutually exclusive group: map or zoomed map
    bg= parser.add_mutually_exclusive_group()
    #World Map Display
    bg.add_argument(
        '-m', '--map',
        help= 'Show Map of the world with forecast location',
        action= "store_true",
        required= False)

    #World Map Display
    bg.add_argument(
        '-z', '--zoom',
        help= 'Show zoomed Map of the world with forecast location',
        action= "store_true",
        required= False)


    #filepath of image to Display. If a folder, choose randomly from that folder. 
    bg.add_argument(
        '-bg', '--bg',
        help= 'Filepath of background image to Display. If a folder, choose randomly from that folder. If the folders have one of the following values: clear-day, clear-night, rain, snow, sleet, wind, fog, cloudy, partly-cloudy-day, or partly-cloudy-night, the appropriate weather icon will be taken from that folder.',
        default= None,
        required= False)



    #InkyWhat
    parser.add_argument(
        '-i', '--inky',
        help= 'Show image on the InkyWhat',
        action= "store_true",
        required= False)



    args= parser.parse_args()


    #test args
    input_dirpath= os.path.join(os.path.dirname(__file__),'saved_weather/sequence1')
    output_dirpath= os.path.join(os.path.dirname(__file__),'outputs/sequence1')
    output_file_prefix= 'test' #optional, default ''
    startframe= 1001 #optional start frame, default-1001
    files= sorted(os.listdir(input_dirpath))
    files=[file for file in files if not file.startswith('.')]
    for frame, file in enumerate(files):
        #forecast= weatherWHAT.getweather(blah, Display save etc)
        input_filename= os.path.join(input_dirpath, file)
        print (input_filename)
        output_basename= '{}{}.png'.format(output_file_prefix, startframe+ frame)
        output_filename= os.path.join(output_dirpath, output_basename)
        try:
            weatherWHAT.display_weather(
                zoom= args.zoom,
                show_on_inky= args.inky, 
                show_image= False, 
                save_image= output_filename, 
                loadforecast= input_filename,
                )

        except ModuleNotFoundError:
            pass


