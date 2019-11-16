#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#put this in a separate file/def:
from PIL import Image, ImageFont, ImageDraw, ImageOps, ImageFilter, ImageEnhance


def mean_of_area(img, x0, y0, x1, y1):
    #get the mean of an area of a Pillow image. Returns a float.
    mean= 0
    for i in range(int(x0), int(x1)):
        for j in range(int(y0), int(y1)):
            px= img.getpixel((i, j))
            mean+= sum(px)/ float(len(px))
            #print (mean)
    mean/= float((x1- x0)* (y1- y0))
    return mean


def roll(image, delta):
    "Roll an image sideways"

    xsize, ysize = image.size

    delta = delta % xsize
    if delta == 0: return image

    part1 = image.crop((0, 0, delta, ysize))
    part2 = image.crop((delta, 0, xsize, ysize))
    image.paste(part2, (0, 0, xsize- delta, ysize))
    image.paste(part1, (xsize-delta, 0, xsize, ysize))

    return image


def clamp(minvalue, value, maxvalue):
    return max(minvalue, min(value, maxvalue))




def choose_bg_from_folder(basedir):
    #choose an images from icons directory
    #returns PILLOW IMAGE object
    import os
    import random

    icons= os.listdir(basedir)
    icons= [icon for icon in icons if os.path.splitext(icon)[-1].lower() in ['.jpg', '.jpeg', '.png', '.gif']]
    #print (icons)
    icon= random.choice(icons)
    saved_image_path= os.path.join(basedir, icon)
    print ("chosen icon:", saved_image_path)
    #load it
    img= Image.open(saved_image_path)
    return img



def load_map(latlong):
    #load map image and draw longitude and latidude lines

    import os

    img= Image.open(os.path.join(os.path.dirname(__file__), 'icons', 'map', 'equirectangular.jpg'))

    img.convert('RGB')
    screen_w, screen_h= img.size

    draw= ImageDraw.Draw(img)


    latitude, longitude= latlong

    #scale latlong to image size:
    longitude= ((longitude/ 360.0)+ .5)* screen_w    

    #screen is inverted in Pillow:
    latitude= (-latitude/ 180.0)+ .5
    latitude*= screen_h


    # Vertical line
    x = int(longitude)
    y_start = 0
    y_end = screen_h
    line = ((x, y_start), (x, y_end))
    draw.line(line, fill= 'black', width= 5)


    # Horizontal line
    y = int(latitude)
    x_start = 0
    x_end = screen_w
    line = ((x_start, y), (x_end, y))
    draw.line(line, fill= 'black', width= 5)

    return img






def load_map_zoom(latlong):
    #load map image and zoom to given latitude and longitude

    import os

    img= Image.open(os.path.join(os.path.dirname(__file__), 'icons', 'map', 'atlas1.jpg'))

    #img= remove_transparency(img)
    img.convert('RGB')#.convert('RGBA')
    screen_w, screen_h= img.size

    #draw= ImageDraw.Draw(img)


    latitude, longitude= latlong

    #scale latlong to image size:
    longitude= ((longitude/ 360.0)+ .5)* screen_w    

    #screen is inverted in Pillow:
    latitude= (-latitude/ 180.0)+ .5
    latitude*= screen_h

    #work out the crops
    left= longitude-(400/ 2)
    right= longitude+(400/ 2)

    upper= latitude-(300/ 2)
    lower= latitude+(300/ 2)



    img= img.crop((left, upper, right, lower))
    return img


def resize_fit(input_image, desired_width, desired_height):
    #args
    #input_image = Image.open("/home/sean.danischevsky/Documents/4.info/pi/icons/sunny.png") 
    #desired_width, desired_height= 400, 300

    bg= Image.new('RGB', (desired_width, desired_height), 'white')
    curr_w, curr_h= input_image.size
    scale_w, scale_h= desired_width/ float(curr_w), desired_height/ float(curr_h)
    scale= min(scale_w, scale_h)

    if scale_w > scale_h:
        new_h= desired_height
        new_w = int(scale*curr_w)


    else:
        new_w= desired_width
        new_h= int(scale*curr_h)
        #print ('padding top and bottom')

    input_image= input_image.resize((new_w, new_h), resample=Image.LANCZOS)
    bg.paste(input_image, box= (int((desired_width- new_w)/ 2.0), int((desired_height- new_h)/ 2.0)), mask=None)
    return bg





def resize_fill(input_image, desired_width, desired_height):
    #args
    #input_image = Image.open("/home/sean.danischevsky/Documents/4.info/pi/icons/sunny.png") 
    #desired_width, desired_height= 400, 300

    bg= Image.new('RGB', (desired_width, desired_height))
    curr_w, curr_h= input_image.size
    scale_w, scale_h= desired_width/ float(curr_w), desired_height/ float(curr_h)
    scale= max(scale_w, scale_h)
    #print ('scaling image by', scale)
    if scale_w < scale_h:
        new_h= desired_height
        new_w= int(scale* curr_w)
        #print ('cropping sides')
    else:
        new_w= desired_width
        new_h= int(scale* curr_h)
        #print ('cropping top and bottom')

    input_image = input_image.resize((new_w, new_h), resample=Image.LANCZOS)
    bg.paste(input_image, box=(int((desired_width- new_w)/ 2.0), int((desired_height- new_h)/ 2.0)), mask=None)
    return bg





def resize_distort(input_image, desired_width, desired_height):
    #args
    #input_image = Image.open("/home/sean.danischevsky/Documents/4.info/pi/icons/sunny.png") 
    #desired_width, desired_height= 400, 300

    return input_image.resize((desired_width, desired_height), resample=Image.LANCZOS)






def remove_transparency(img, bg_colour= (255, 255, 255)):
    # replaces transparent pixels with color
    #Only process if image has transparency (http://stackoverflow.com/a/1963146)
    #input = PIL image
    #output = PIL image with mode 'RGB'
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):

        # Need to convert to RGBA if LA format due to a bug in PIL (http://stackoverflow.com/a/1963146)
        alpha = img.convert('RGBA').split()[-1]

        # Create a new background image of our matt color.
        bg= Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, img)
        return bg

    else:
        return img



def inky_dither(img):
    #traditional dither for inky
    palette=[
        0, 0, 0, # index 0 is black
        255, 255, 255, # index 1 is white
        255, 255, 0, ]   # index 2 is yellow

    # Convert the image to use a white / black / red colour palette
    pal_img = Image.new("P", (1, 1))
    pal_img.putpalette((255, 255, 255, 0, 0, 0, 200, 200, 0)+ (0, 0, 0)* 252)#yellow
    img= img.convert("RGB", 0).quantize(palette= pal_img)
    return img




def inky_dither_sean(img):

    import matplotlib.pyplot as plt
    import numpy as np
    from PIL import Image, ImageFont, ImageDraw

    
    

    
    #define palette colors
    black= [0,10,30]
    white= [255,255,255]
    yellow= [200,200,0]
    colors= [black, white, yellow]

    def closest(colors, color):

        import random
        import math

        #find closest 
        colors = np.array(colors)
        color = np.array(color)
        distances = np.sqrt(np.sum((colors-color)** 2,axis= 1))

        #normalize
        distances-= min(distances)
        distances/= max(distances)

        #distances=[i-min(distances) for i in distances]
        #distances=[i/float(max(distances)) for i in distances]

        #reverse
        distances=[1- i  for i in distances]
        buckets= 3
        my_list = [colors[0]]* math.floor(distances[0]* buckets)+ [colors[1]]* math.floor(distances[1]* buckets)+ [colors[2]]* math.floor(distances[2]*buckets)
               
        #index_of_smallest= np.where(distances== np.amin(distances))
        #smallest_distance= colors[index_of_smallest]
        return random.choice(my_list)


    w, h= img.size        

    for i in range(w):
        for j in range(h):
            color= img.getpixel((i, j))
            nearest= closest(colors, color)
            img.putpixel((i,j), (tuple(nearest)) )
    return inky_dither(img) #flatten it the only way I know how




def reflow_summary(summary, width, font):
    words= summary.split(" ")
    reflowed= ''
    line_length= 0

    for i in range(len(words)):
        word= words[i]+ " "
        word_length= font.getsize(word)[0]
        line_length += word_length

        if line_length < width:
            reflowed+= word
        else:
            line_length= word_length
            reflowed= reflowed[:-1]+ "\n  "+ word

    reflowed= reflowed.rstrip()+ ''

    return reflowed




def summary_font_loader(size):
    #load font for weather summary

    import os

    try:
        #print(1)
        from font_source_sans_pro import SourceSansProSemibold
        font= ImageFont.truetype(SourceSansProSemibold, size)
    except:
        #print(2)
        try:
            #print(3)
            font= ImageFont.truetype("arial.ttf", size)
        except: 
            try:
                #print(4)
                font= ImageFont.truetype(os.path.join(os.path.dirname(__file__), 'fonts', 'SourceSansPro-Semibold.ttf'), size)
            except:
                #print(5)
                font= ImageFont.load_default()
    return font







def temperature_font_loader(size):

    #load font for temperature display

    import os

    try:
        #print('t1')
        from font_hanken_grotesk import HankenGroteskBold#, HankenGroteskMedium
        font= ImageFont.truetype(HankenGroteskBold, size)
    except:
        #print('t2')
        try:
            #print('t3')
            font= ImageFont.truetype("arial.ttf", size)
        except: 
            try:
                #print('t4')
                font= ImageFont.truetype(os.path.join(os.path.dirname(__file__), 'fonts','SourceSansPro-Semibold.ttf'), size)
            except:
                #print('t5')
                font= ImageFont.load_default()
    return font



def setup_inky(inky_colour):
    from inky import InkyWHAT

    inky_display= InkyWHAT(inky_colour)
    ink_white= inky_display.WHITE    #0
    ink_black= inky_display.BLACK    #1
    ink_color= inky_display.YELLOW   #2
    
    inky_display.set_border(inky_display.WHITE)

    w= inky_display.WIDTH
    h= inky_display.HEIGHT

    return w, h, ink_black, ink_color #,fonts_dict


def setup_screen():
    w, h= 400, 300
    ink_color= 2
    ink_black= 1

    return w,h, ink_black, ink_color #,fonts_dict





def write_in_box(img, x0, y0, x1, y1, msg, initial_scale, font, fill= None, spacing= 0, align_x= "center", align_y= "center"):

    #splits lines to fit the aspect ratio of the input box

    import textwrap
    import math

    if msg:
        max_width= x1- x0
        max_height= y1- y0
        aspect= (x1- x0)/ float(y1- y0)
        reflowed= [msg]
        lines= 1
        
        p_w, p_h= max((font.getsize(line) for line in reflowed))# Width and height of summary
        p_h= p_h* (len(reflowed))   # Multiply through by number of lines
   
        reflowed_aspect= (p_w)/ float(p_h)

        while reflowed_aspect > aspect and lines < 100:
            #reflow text to make the x shorter
            lines+= 1
            reflowed = textwrap.wrap(msg, width= math.ceil(len(msg)* 1.05/ float(lines)))  #fudge because textwrap sometimes gives too many lines here
            #print (reflowed)
            #print (lines)
            p_w, p_h= max((font.getsize(line) for line in reflowed))# Width and height of summary
            p_h= p_h* (len(reflowed))   # Multiply through by number of lines    
            reflowed_aspect= (p_w)/ float(p_h)
        else:
            #we've gone too far, go back!
            if lines > 1:
                lines-= 1
            reflowed= textwrap.wrap(msg, width= math.ceil(len(msg)/ float(lines)))
            p_w, p_h= max((font.getsize(line) for line in reflowed))# Width and height of summary
            p_h= p_h* (len(reflowed))   # Multiply through by number of lines    
            reflowed_aspect= (p_w)/ float(p_h)

        scale_adjust= 0

        while (p_w > max_width) or (p_h > max_height) and (initial_scale+ scale_adjust) > 1: #to stop endles loops
            #scale text to fit
            #print (scale_adjust,  initial_scale,  initial_scale- scale_adjust)
            scale_adjust-= 1
            font= summary_font_loader(int(initial_scale+ scale_adjust))
            p_w, p_h= max((font.getsize(line) for line in reflowed))# Width and height of summary
            p_h= p_h* (len(reflowed))   # Multiply through by number of lines
            #print ("pw,ph",p_w, p_h)


        centerline= (max_width- p_w)/ 2.0 #-helf a letter
        #print (centerline)
        reflowed= "\n".join(reflowed)
        #print (reflowed)
        if align_y == "top":
            topline= y0
        elif align_y == "bottom":
            topline= y1- p_h
        else:
            topline= ((y1- y0)/ 2.0)- p_h




        bg= Image.new("RGBA", img.size, color= (0, 0, 0, 0))

        draw= ImageDraw.Draw(bg)
        draw.text((centerline, topline), reflowed, fill= fill, font= font, spacing= spacing, align= align_x)
        
        outline= bg.filter(ImageFilter.MaxFilter(size= 3)).filter(ImageFilter.GaussianBlur(5))
        strongshadow= bg.filter(ImageFilter.GaussianBlur(25))
        softshadow= bg.filter(ImageFilter.GaussianBlur(50))

        img.paste("white", mask= outline)   
        img.convert("RGB")
        img.paste("white", mask= softshadow)   
        img.convert("RGB")
        img.paste("white", mask= strongshadow)  
        img.convert("RGB")

        img.paste(bg, mask= bg)
        img.convert("RGB")

        return img




def text_box(img, x0, y0, x1, y1, msg, initial_scale, font, fill= None, spacing= 0, align_x= "center", align_y= "center"):
    #write a single line in a text box
    #return final coordinates of text on image
    if msg:
        max_width= x1- x0
        max_height= y1- y0

        scale_adjust= 0

        temperature_font= temperature_font_loader(int(initial_scale))
        temperature_w, temperature_h= font.getsize(msg)

        while (temperature_w > max_width ) or ( temperature_h > max_height ) and ((initial_scale+ scale_adjust) > 1):

            scale_adjust-= 1
            font= temperature_font_loader(int(initial_scale+ scale_adjust))   #MUST CHANGE THIS
            new_w, new_h= temperature_font.getsize(msg)
            if (new_w, new_h) == (temperature_w, temperature_h):
                break
            else:
                temperature_w, temperature_h= temperature_font.getsize(msg)

        temperature_x= int((max_width- temperature_w)/ 2)
        temperature_y= int((max_height- temperature_h)/ 2)#0#+ padding


        bg= Image.new("RGBA", img.size, color= (255, 255, 0, 0))


        draw= ImageDraw.Draw(bg)
        draw.text((temperature_x, temperature_y), msg, fill= (255, 255, 0, 255), font= font)

        
        strongshadow= bg.filter(ImageFilter.GaussianBlur(25))

        softshadow= bg.filter(ImageFilter.GaussianBlur(50))
        img.paste("white", mask= softshadow)
        img.convert("RGB")
        img.paste("white", mask= strongshadow)  
        img.convert("RGB")
        img.paste(bg, mask= bg)
        img.convert("RGB")

        return temperature_x, temperature_y, temperature_x+ temperature_w, temperature_y+ temperature_h



def median_dict(d):
    
    from collections import OrderedDict
    import statistics
    values_sorted = OrderedDict(sorted(d.items(), key=lambda t: t[1]))
    index = sum(values_sorted.values())/2

    # Decide whether the number of records is an even or odd number
    if (index).is_integer():
        even = True
    else: 
        even = False

    x = True

    # Compute median
    for value, occurences in values_sorted.items():
        index -= occurences
        if index < 0 and x is True:
            median_manual = value
            break
        elif index == 0 and even is True:
            median_manual = value/ 2
            x = False
        elif index < 0 and x is False:

            median_manual += value/ 2
            break

    # Create a list of all records and compute median using statistics package
    values_list= list()
    for val, count in d.items():
        for count in range(count):
            values_list.append(val)

    median_computed = statistics.median(values_list)

    return median_computed



def mean_dict(a):

    mean= sum(a.values())/ 2.0
    
    #forwards
    sum_a= 0
    vals= sorted(a.items())
    for k,v in vals:
        #print k,v
        sum_a+= v
        if sum_a >= mean:
            break 
    answer1= k

    #backwards
    sum_a= 0
    for k, v in reversed(vals):
        
        sum_a+= v
        if sum_a >= mean:
            break 
    answer2= k
    #print answer1, answer2


    answer_index= int(round((answer1+ answer2)/ float(2)))

    #print "ANSWER", vals[answer_index]

    return answer_index



def mean_x(img):
    #calculate the centroid in x
    width, height= img.size
    for x in range(width):
        y_= {} #xval: sum
        sum_y= 0
        for y in range(height):
            sum_y+= sum(img.getpixel((x, y))) #sum of y
            y_[y]= sum_y #sum of channels
    

    #median_val= sum_y/ 2
    mean_val= mean_dict(y_)

    #print ("mean", mean_val)
    return mean_val





def text_box2(img, x0, y0, x1, y1, msg, initial_scale, font, fill= None, spacing= 0, align_x= "center", align_y= "center"):
    #write a single line in a text box
    #center uses median value
    #return final coordinates of text on image
    #print ( x0,  x1)
    if msg:
        max_width= x1- x0
        max_height= y1- y0

        scale_adjust= 0

        temperature_font= temperature_font_loader(int(initial_scale))
        temperature_w, temperature_h= font.getsize(msg)

        while (temperature_w > max_width ) or ( temperature_h > max_height ) and ((initial_scale+ scale_adjust) > 1):

            scale_adjust-= 1
            font= temperature_font_loader(int(initial_scale+ scale_adjust))   #MUST CHANGE THIS
            new_w, new_h= temperature_font.getsize(msg)
            if (new_w, new_h) == (temperature_w, temperature_h):
                break
            else:
                temperature_w, temperature_h= temperature_font.getsize(msg)

        temperature_x= 0#int((max_width- temperature_w)/ 2)
        #print ('temperature_x',temperature_x)
        temperature_y= int((max_height- temperature_h)/ 2)

        #yellow
        bg= Image.new("RGBA", img.size, color= (255, 255, 0, 0))
        draw= ImageDraw.Draw(bg)
        draw.text((temperature_x, temperature_y), msg, fill= (255, 255, 0, 255), font= font)

        #update with median 
        #temperature_x = int(x0+ (mean_x(bg))  )
        temperature_x= int((x0+ mean_x(bg)- temperature_w/ 2.0))
        #print ('new temperature_x', temperature_x)

        bg= Image.new("RGBA", img.size, color= (255, 255, 0, 0))
        draw= ImageDraw.Draw(bg)
        draw.text((temperature_x, temperature_y), msg, fill= (255, 255, 0, 255), font= font)        
        
        strongshadow= bg.filter(ImageFilter.GaussianBlur(25))

        softshadow= bg.filter(ImageFilter.GaussianBlur(50))
        img.paste("white", mask= softshadow)
        img.convert("RGB")
        img.paste("white", mask= strongshadow)  
        img.convert("RGB")
        img.paste(bg, mask= bg)
        img.convert("RGB")

        return temperature_x, temperature_y, temperature_x+ temperature_w, temperature_y+ temperature_h











def main(forecast, 
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
    verbose):


    import os
    import datetime

    #choose and format data for image display

    #don't use temperature_high_time= forecast.daily.data[0].temperature_high_time
    #because high for the next day would appear after midnight
    #and I wanted to see the low at 7am (or whenever it was still coming)
    high= max(forecast.hourly.data[:24], key= lambda x: x.temperature)
    low= min(forecast.hourly.data[:24], key= lambda x: x.temperature)


    

    #daily[0] = TODAY
    sunrise_time= forecast.daily.data[0].sunrise_time
    sunset_time= forecast.daily.data[0].sunset_time

    temperature_msg= str(round(forecast.currently.temperature))+ "°"






    #hi/lo 

    if (low.time < high.time) and low.time- forecast.currently.time > datetime.timedelta(hours= 1):# and (low.time- forecast.currently.time).seconds > datetime.timedelta(hours= 1).seconds: 
        high_next= False 
        hi_lo_msg= "low {}°\n{}".format(str(round(low.temperature)), low.time.strftime("%H:%M"))

    else:
        #high time is next 
        high_next= True
        hi_lo_msg= "high {}°\n{}".format(str(round(high.temperature)), high.time.strftime("%H:%M"))    

   





    #sunrise/sunset time
    try:
        if (sunrise_time < forecast.currently.time < sunset_time):
            #it's day time            
            sun_msg= "sunset\n{}".format(sunset_time.strftime("%H:%M"))
            summary= forecast.hourly.summary.rstrip(".")

        else:
            # night time
            sun_msg= "sunrise\n{}".format(sunrise_time.strftime("%H:%M"))
            summary= forecast.daily.summary.rstrip(".")
    except:
        #We're at the North pole and there's no sunset
        sun_msg= ""
        summary= forecast.hourly.summary.rstrip(".")



    #replace summary with soonest alert
    alerts= forecast.alerts
    if alerts:
        min_alert= min(alerts, key= lambda x: x.time)
        alert= "{}: {}".format(min_alert.time.strftime("%A %H:%M"), min_alert.title)
    else:
        alert= None


    if alert:
        summary= alert #replace summary with alert    


    #here is where you could do a check to see if the screen needs updating-
    #save old version and if new != old, update

    # create display image



    # Set up the correct display and scaling factors
    try:
        w, h, ink_black, ink_color= setup_inky(inky_colour)
    except:
        #go_to_screen= True# ...get screen size?
        w, h, ink_black, ink_color= setup_screen()



    #setup canvas
    try:
        if bg_file:

        #user has specified a background
            if os.path.isfile(bg_file):
                #load image from absolute file path or file path relative to their location
                img= Image.open(bg_file)
             
            elif os.path.isfile(os.path.join(os.path.dirname(__file__), bg_file)):
                #load file relative to this script
                img= Image.open(os.path.join(os.path.dirname(__file__), bg_file))

            elif os.path.isdir(bg_file):
                #choose icon from named structure within folder
                #the dirs are icon names
                basedir= os.path.join(bg_file, forecast.currently.icon)
                if os.path.isdir(basedir):
                    img= choose_bg_from_folder(basedir)

                else:
                    #choose random bg from folder
                    img= choose_bg_from_folder(bg_file)


            elif os.path.isdir(os.path.join(os.path.dirname(__file__), bg_file)):
                #choose icon from named structure within folder
                #the dirs are icon names
                basedir= os.path.join(os.path.join(os.path.dirname(__file__), bg_file), forecast.currently.icon)
                if os.path.isdir(basedir):
                    img= choose_bg_from_folder(basedir)

                else:
                    #choose random bg from folder
                    img= choose_bg_from_folder(os.path.join(os.path.dirname(__file__), bg_file))

            else:
                print ("Can't load \n{}\n as background. Please specify a directory or filename. Try using an absolute path?".format(os.path.abspath(bg_file)))

            img= remove_transparency(img)
            img= resize_fill(img, w, h) 




        elif bg_map:
            #load map image
            img= load_map(latlong)   
            img= resize_distort(img, w, h) 
        elif zoom:
            #load zoomed map image
            img= load_map_zoom(latlong)
            
        else:
            #choose from default icon list
            basedir= os.path.join(os.path.dirname(__file__), 'icons','default', forecast.currently.icon)
            img= choose_bg_from_folder(basedir)
            img= resize_fill(img, w, h) 

    except Exception as e:
        print(e, ": using blank background.")

        #blank bg
        img= Image.new("RGB", (w, h), color=(255, 255, 255))



    #add soft white top and bottom
    softshadow= Image.new("RGBA", (w, h), color= (255, 255, 255, 255))
    draw= ImageDraw.Draw(softshadow)
    draw.rectangle((0, 10, w, h- 50), fill= (0, 0, 0, 0))


    #strongshadow= bg.filter(ImageFilter.GaussianBlur(25))

    softshadow= softshadow.filter(ImageFilter.GaussianBlur(50))
    img.paste("white", mask= softshadow)   
    img.convert("RGB")


    draw= ImageDraw.Draw(img)


    # messages at top of screen: banner, location_banner, forecast time

    top_line= 0
    # banner
    if banner:
        img= write_in_box(img, 0, 0, 400, 40, banner, 20, summary_font_loader(20), fill= (0, 0, 0, 255), spacing= 0, align_x= "center", align_y= "top")
        top_line+= 25
    # location_banner
    if location_banner:
        img= write_in_box(img, 0, top_line, 400, 40+top_line, location_banner, 20, summary_font_loader(20), fill= (0, 0, 0, 255), spacing= 0, align_x= "center", align_y= "top")
        top_line+= 25

    # forecast time
    img= write_in_box(img, 0, top_line, 400, 40+top_line, forecast.currently.time.strftime("%A %d %b %Y"), 20, summary_font_loader(20), fill= (0, 0, 0, 255), spacing= 0, align_x= "center", align_y= "top")


    
    
    #current temperature
    x0, y0, x1, y1= text_box2(img, 0, 0, w, h- 90, temperature_msg, int(50* 2.2), temperature_font_loader(int(50* 2.2)), 
        fill= (255, 255, 0, 255), spacing= 0, align_x= "center", align_y= "center")


    temperature_y= (y1- y0)/ 2





    #HI/Lo on LHS MIDDLE
    padding= 50
    max_width= w- padding
    max_height= 250
    font_size= 24
    below_max_length= False
    scale_adjust= 1
    msg= hi_lo_msg

    while not below_max_length:
        summary_font= summary_font_loader(font_size* scale_adjust)
        reflowed= reflow_summary(msg, max_width, summary_font)
        p_w, p_h= summary_font.getsize(reflowed)  # Width and height of summary
        p_h= p_h* (reflowed.count("\n")+ 1)   # Multiply through by number of lines

        if p_h < max_height:
            below_max_length= True              # The summary fits! Break out of the loop.
        else:
            # scale down text to fit 
            scale_adjust*= .95

    # x- and y-coordinates for the top left of the summary
    summary_x= 5   #do i need to check for the longest linw and get size of that?
    summary_y= temperature_y+ 48

    #draw it now
    bg= Image.new("RGBA", img.size, color= (0, 0, 0, 0))


    draw= ImageDraw.Draw(bg)

    if mean_of_area(img, summary_x, summary_y, summary_x+ p_w, summary_y+ p_h) > .5* 255:
        #area is white, use black text and white shadow
        fill= (0, 0, 0, 255)
        shadowfill= (255, 255, 255)
    else:
        fill= (255, 255, 255, 255)
        shadowfill= (0, 0, 0)  

    draw.multiline_text((summary_x, summary_y), reflowed, fill= fill, font= summary_font, align= "left")
    
    strongshadow= bg.filter(ImageFilter.GaussianBlur(25))

    softshadow= bg.filter(ImageFilter.GaussianBlur(50))
    img.paste(shadowfill, mask= softshadow)   
    img.convert("RGB")
    img.paste(shadowfill, mask= strongshadow)  
    img.convert("RGB")
    img.paste(bg, mask= bg)
    img.convert("RGB")





    draw= ImageDraw.Draw(img)



    
    #sunrise/sunset on RHS MIDDLE
    padding= 0
    max_width= w- padding
    max_height= 250
    font_size= 24
    below_max_length= False
    scale_adjust= 1
    msg= sun_msg

    if msg:
        while not below_max_length:
            summary_font= summary_font_loader(font_size* scale_adjust)
            reflowed= reflow_summary(msg, max_width, summary_font)
            p_w, p_h= max((summary_font.getsize(line) for line in reflowed.splitlines())) # Width and height of summary
            p_h= p_h* (reflowed.count("\n")+ 1)   # Multiply through by number of lines

            if p_h < max_height:
                below_max_length= True              # The summary fits! Break out of the loop.
            else:
                # scale down text to fit 
                scale_adjust*= .95

        # x and y coordinates for the top left of the summary
        summary_x= w- p_w- 5
        summary_y= temperature_y+ 48

        bg= Image.new("RGBA", img.size, color= (0, 0, 0, 0))


        draw= ImageDraw.Draw(bg)
        #print (mean_of_area(img, summary_x, summary_y, summary_x+ p_w, summary_y+ p_h))
        if mean_of_area(img, summary_x, summary_y, summary_x+ p_w, summary_y+ p_h)> .5* 255:
            #area is white, use black text and white shadow
            fill= (0, 0, 0, 255)
            shadowfill= (255, 255, 255)
        else:
            fill= (255, 255, 255, 255)
            shadowfill= (0, 0, 0)               
        draw.multiline_text((summary_x, summary_y), reflowed, fill= fill, font= summary_font, align= "right")

        strongshadow= bg.filter(ImageFilter.GaussianBlur(25))
        softshadow= bg.filter(ImageFilter.GaussianBlur(50))


        img.paste(shadowfill, mask= softshadow)   
        img.convert("RGB")
        img.paste(shadowfill, mask= strongshadow)  
        img.convert("RGB")
        img.paste(bg, mask= bg)
        img.convert("RGB")



    

    #rain graphic / sun (UV) strength

    y0= 0
    y1= 130

    rain_img= Image.new("RGBA", (w, y1), color= (255, 255, 255, 0))
    draw= ImageDraw.Draw(rain_img)
    font= summary_font_loader(14)

    for i, hour in enumerate(forecast.hourly.data[:24]):
        t= hour.time.strftime("%H")
        p= int(hour.precip_probability* hour.precip_intensity* 25500) #should be x 255
        if verbose:
            print (hour.time.strftime("%A %d %b %Y %H:%M"), hour.precip_probability, hour.precip_intensity)                
            if p:
                print (hour.precip_type, p)
        x0= int(w/ 24* i)
        x1= int(w/ 24* (i+ 1))
        #pcolor=255- p
        pcolor= int(hour.precip_probability* 255* .5) #.5 is a fade factor - don't want bars too strong
        #tcolor=(pcolor+ 128)% 255
        tcolor= 0                
        if p:#>17:#>17 gives a value when inkied
            #amount and probability of rain
            #the /2 means scale london weather down to look good - your country may vary
            #rain_indicator
            draw.rectangle((x0, y1- 16- 1, x1- 1, y1- 16- 3), fill= (0, 0, 0, p))#color), outline= (0, 0, 0, p))

            #rain bars
            draw.rectangle((x0, clamp(y0, y1- (hour.precip_intensity/ 2* (y1- y0)), y1- 16), x1- 1, y1- 16), fill= (0, 0, 0, pcolor), outline= (0, 0, 0, 255))
        



        #UV rectangles
        if hour.uv_index:            
            
            if hour.uv_index == 1:
                uv= int(255* .025)
            elif hour.uv_index == 2:
                uv= int(255* .05)
            elif hour.uv_index == 3:
                uv= int(255* .075)
            else:
                uv= (hour.uv_index > 3)* 255
            draw.rectangle((x0, y1, x1- 1, y1- 16), fill= (255, 255, 255, 255), outline= (0, 0, 0, 255))
            draw.rectangle((x0, y1, x1- 1, y1- 16), fill= (255, 255, 0, uv), outline= (0, 0, 0, 255))

        draw.text((x0+ 2, y0- 16+ y1), str(t), fill= (0, 0, 0, 255), font= font, align= 'center') #added a plus one to look better lined up
        

        img.paste(rain_img, box= (0, 300- y1), mask= rain_img)

    img.convert("RGB")




    #forecast hourly summary at bottom
    img= write_in_box(img, 0, 280- 120, 400, 270, summary, 20, summary_font_loader(20), fill= (0, 0, 0, 255), spacing= 0, align_x= "center", align_y= "bottom")

    #print(img.mode)

    if show_on_inky:
        #dither before saving or displaying
        img.convert("RGB")
        img= inky_dither(img)


    if save_image:
        img.convert("RGB")
        #save image
        img.save(save_image)
        print (save_image)



    if show_image:
        img.convert("RGB", 0)
        #show image
        img.show()




    # Display the completed canvas on Inky wHAT
    if show_on_inky:
        from inky import InkyWHAT
        inky_display= InkyWHAT(inky_colour)

        inky_display.set_image(img)
        #To Show upside down inky_display.set_image(img.rotate(180))      

        inky_display.show()






