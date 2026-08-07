#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image, ImageFont, ImageDraw, ImageFilter


def _sz(font, t):
    # Pillow 10+ removed FreeTypeFont.getsize(). Emulate its (width, height)
    # return value using getbbox().
    l, tp, r, b = font.getbbox(t)
    return r - l, b - tp


def load_icon(name, px):
    # load a bundled icon PNG (icons/<subdir>/<name>.png) scaled to `px` TALL,
    # preserving aspect ratio (square meteocons stay square; the tall thermometers
    # stay narrow). meteocons = sun/moon phases; gauge = the min/max thermometers.
    import os
    base = os.path.join(os.path.dirname(__file__), 'icons')
    for sub in ('meteocons', 'gauge'):
        path = os.path.join(base, sub, name + '.png')
        if os.path.isfile(path):
            im = Image.open(path).convert("RGBA")
            w0, h0 = im.size
            return im.resize((max(1, round(px * w0 / h0)), px), Image.LANCZOS)
    raise FileNotFoundError("icon not found: " + name)


def mono_icon(icon, rgb):
    # flatten an icon to a solid black/white silhouette (using its alpha as the
    # shape) so it matches the monochrome text — colour chosen by the background.
    alpha= icon.split()[-1]
    solid= Image.new("RGBA", icon.size, (rgb[0], rgb[1], rgb[2], 255))
    solid.putalpha(alpha)
    return solid


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
    #choose an images from backgrounds directory

    import os
    import random

    backgrounds= os.listdir(basedir)
    backgrounds= [background for background in backgrounds if os.path.splitext(background)[-1].lower() in ['.jpg', '.jpeg', '.png', '.gif']]
    #print (backgrounds)
    background= random.choice(backgrounds)
    saved_image_path= os.path.join(basedir, background)
    return saved_image_path



def load_map(lat, lon):
    #load map image and draw longitude and latidude lines

    import os

    img= Image.open(os.path.join(os.path.dirname(__file__), 'backgrounds', 'map', 'equirectangular.jpg'))

    img.convert('RGB')
    screen_w, screen_h= img.size

    draw= ImageDraw.Draw(img)

    #scale latlong to image size:
    lon= ((lon/ 360.0)+ .5)* screen_w    

    #screen is inverted in Pillow:
    lat= (-lat/ 180.0)+ .5
    lat*= screen_h


    # Vertical line
    x = int(lon)
    y_start = 0
    y_end = screen_h
    line = ((x, y_start), (x, y_end))
    draw.line(line, fill= 'black', width= 5)


    # Horizontal line
    y = int(lat)
    x_start = 0
    x_end = screen_w
    line = ((x_start, y), (x_end, y))
    draw.line(line, fill= 'black', width= 5)

    return img






def load_map_zoom(lat, lon, w, h):
    #load map image and zoom to given latitude and longitude

    import os

    img= Image.open(os.path.join(os.path.dirname(__file__), 'backgrounds', 'map', 'atlas1.jpg'))

    #img= remove_transparency(img)
    img.convert('RGB')#.convert('RGBA')
    screen_w, screen_h= img.size

    #scale latlong to image size:
    lon= ((lon/ 360.0)+ .5)* screen_w    

    #screen is inverted in Pillow:
    lat= (-lat/ 180.0)+ .5
    lat*= screen_h

    #work out the crops
    left= lon- (w/ 2)
    right= lon+ (w/ 2)

    upper= lat- (h/ 2)
    lower= lat+ (h/ 2)

    img= img.crop((left, upper, right, lower))
    return img


def resize_fit(input_image, desired_width, desired_height):
    #args
    #input_image = Image.open("/home/sean.danischevsky/Documents/4.info/pi/backgrounds/sunny.png") 
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
    #input_image = Image.open("/home/sean.danischevsky/Documents/4.info/pi/backgrounds/sunny.png") 
    #desired_width, desired_height= 400, 300

    bg= Image.new('RGB', (desired_width, desired_height))
    curr_w, curr_h= input_image.size
    scale_w, scale_h= desired_width/ float(curr_w), desired_height/ float(curr_h)
    scale= max(scale_w, scale_h)
    #print ('scaling image by', scale)
    if scale_w < scale_h:
        #crop sides
        new_h= desired_height
        new_w= int(scale* curr_w)
    else:
        # crop top and bottom
        new_w= desired_width
        new_h= int(scale* curr_h)

    input_image = input_image.resize((new_w, new_h), resample=Image.LANCZOS)
    bg.paste(input_image, box=(int((desired_width- new_w)/ 2.0), int((desired_height- new_h)/ 2.0)), mask=None)
    return bg





def resize_distort(input_image, desired_width, desired_height):
    #args
    #input_image = Image.open("/home/sean.danischevsky/Documents/4.info/pi/backgrounds/sunny.png") 
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

        #reverse
        distances=[1- i  for i in distances]
        buckets= 3
        my_list = [colors[0]]* math.floor(distances[0]* buckets)+ [colors[1]]* math.floor(distances[1]* buckets)+ [colors[2]]* math.floor(distances[2]*buckets)
               
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
        word_length= _sz(font, word)[0]
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
        try:
            font= ImageFont.truetype("arial.ttf", size)
        except: 
            try:
                font= ImageFont.truetype(os.path.join(os.path.dirname(__file__), 'fonts', 'SourceSansPro-Semibold.ttf'), size)
            except:
                font= ImageFont.load_default()
    return font







def temperature_font_loader(size):

    #load font for temperature display

    import os

    try:
        from font_hanken_grotesk import HankenGroteskBold#, HankenGroteskMedium
        font= ImageFont.truetype(HankenGroteskBold, size)
    except:
        try:
            font= ImageFont.truetype("arial.ttf", size)
        except: 
            try:
                font= ImageFont.truetype(os.path.join(os.path.dirname(__file__), 'fonts','SourceSansPro-Semibold.ttf'), size)
            except:
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

    return w, h, ink_black, ink_color #,fonts_dict





def write_in_box(img, x0, y0, x1, y1, msg, initial_scale, font, fill= None, spacing= 0, align_x= "center", align_y= "center", scale= 1.0):

    #splits lines to fit the aspect ratio of the input box

    import textwrap
    import math

    if msg:
        max_width= x1- x0
        max_height= y1- y0
        aspect= (x1- x0)/ float(y1- y0)
        reflowed= [msg]
        lines= 1
        
        p_w, p_h= max((_sz(font, line) for line in reflowed))# Width and height of summary
        p_h= p_h* (len(reflowed))   # Multiply through by number of lines
   
        reflowed_aspect= (p_w)/ float(p_h)

        while reflowed_aspect > aspect and lines < 100:
            #reflow text to make the x shorter
            lines+= 1
            reflowed = textwrap.wrap(msg, width= math.ceil(len(msg)* 1.05/ float(lines)))  #fudge because textwrap sometimes gives too many lines here
            p_w, p_h= max((_sz(font, line) for line in reflowed))# Width and height of summary
            p_h= p_h* (len(reflowed))   # Multiply through by number of lines    
            reflowed_aspect= (p_w)/ float(p_h)
        else:
            #we've gone too far, go back!
            if lines > 1:
                lines-= 1
            reflowed= textwrap.wrap(msg, width= math.ceil(len(msg)/ float(lines)))
            p_w, p_h= max((_sz(font, line) for line in reflowed))# Width and height of summary
            p_h= p_h* (len(reflowed))   # Multiply through by number of lines    
            reflowed_aspect= (p_w)/ float(p_h)

        scale_adjust= 0

        while (p_w > max_width) or (p_h > max_height) and (initial_scale+ scale_adjust) > 1: #to stop endles loops
            #scale text to fit
            scale_adjust-= 1
            font= summary_font_loader(int(initial_scale+ scale_adjust))
            p_w, p_h= max((_sz(font, line) for line in reflowed))# Width and height of summary
            p_h= p_h* (len(reflowed))   # Multiply through by number of lines

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
        
        max_sz= max(3, int(3* scale) | 1)   # MaxFilter needs an odd int >= 3
        outline= bg.filter(ImageFilter.MaxFilter(size= max_sz)).filter(ImageFilter.GaussianBlur(5* scale))
        strongshadow= bg.filter(ImageFilter.GaussianBlur(25* scale))
        softshadow= bg.filter(ImageFilter.GaussianBlur(50* scale))

        img.paste("white", mask= outline)   
        img.convert("RGB")
        img.paste("white", mask= softshadow)   
        img.convert("RGB")
        img.paste("white", mask= strongshadow)  
        img.convert("RGB")

        img.paste(bg, mask= bg)
        img.convert("RGB")

        return img




def text_box(img, x0, y0, x1, y1, msg, initial_scale, font, fill= None, spacing= 0, align_x= "center", align_y= "center", scale= 1.0):
    #write a single line in a text box
    #return final coordinates of text on image
    if msg:
        max_width= x1- x0
        max_height= y1- y0

        scale_adjust= 0

        temperature_font= temperature_font_loader(int(initial_scale))
        temperature_w, temperature_h= _sz(font, msg)

        while (temperature_w > max_width ) or ( temperature_h > max_height ) and ((initial_scale+ scale_adjust) > 1):

            scale_adjust-= 1
            font= temperature_font_loader(int(initial_scale+ scale_adjust))   #MUST CHANGE THIS
            new_w, new_h= _sz(temperature_font, msg)
            if (new_w, new_h) == (temperature_w, temperature_h):
                break
            else:
                temperature_w, temperature_h= _sz(temperature_font, msg)

        temperature_x= int((max_width- temperature_w)/ 2)
        temperature_y= int((max_height- temperature_h)/ 2)#0#+ padding


        bg= Image.new("RGBA", img.size, color= (255, 255, 0, 0))


        draw= ImageDraw.Draw(bg)
        draw.text((temperature_x, temperature_y), msg, fill= (255, 255, 0, 255), font= font)

        
        strongshadow= bg.filter(ImageFilter.GaussianBlur(25* scale))

        softshadow= bg.filter(ImageFilter.GaussianBlur(50* scale))
        img.paste("white", mask= softshadow)
        img.convert("RGB")
        img.paste("white", mask= strongshadow)
        img.convert("RGB")
        img.paste(bg, mask= bg)
        img.convert("RGB")

        # return the TRUE rendered ink box (accounts for the font's top/bottom
        # bearings) so callers get the real on-screen top/bottom of the number.
        # (y1-y0) is unchanged vs the old return, so text-mode callers that use
        # (y1-y0)/2 are unaffected; icon mode relies on the accurate bottom.
        ink= draw.textbbox((temperature_x, temperature_y), msg, font= font)
        return ink[0], ink[1], ink[2], ink[3]



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





def text_box2(img, x0, y0, x1, y1, msg, initial_scale, font, fill= None, spacing= 0, align_x= "center", align_y= "center", scale= 1.0):
    #write a single line in a text box
    #center uses median value
    #return final coordinates of text on image
    #print ( x0,  x1)
    if msg:
        max_width= x1- x0
        max_height= y1- y0

        scale_adjust= 0

        temperature_font= temperature_font_loader(int(initial_scale))
        temperature_w, temperature_h= _sz(font, msg)

        while (temperature_w > max_width ) or ( temperature_h > max_height ) and ((initial_scale+ scale_adjust) > 1):

            scale_adjust-= 1
            font= temperature_font_loader(int(initial_scale+ scale_adjust))   #MUST CHANGE THIS
            new_w, new_h= _sz(temperature_font, msg)
            if (new_w, new_h) == (temperature_w, temperature_h):
                break
            else:
                temperature_w, temperature_h= _sz(temperature_font, msg)

        # Centre the glyph ink horizontally in the box using its real bbox
        # (l is the left bearing). The old mean_x() centroid effectively
        # returned ~height/2, so the temperature only looked centred on a
        # near-square 4:3 panel and drifted left as the canvas got wider.
        l, tp, r, b= font.getbbox(msg)
        temperature_w= r- l
        temperature_h= b- tp
        temperature_x= int(x0+ (max_width- temperature_w)/ 2- l)
        temperature_y= int((max_height- temperature_h)/ 2)

        #yellow
        bg= Image.new("RGBA", img.size, color= (255, 255, 0, 0))
        draw= ImageDraw.Draw(bg)
        draw.text((temperature_x, temperature_y), msg, fill= (255, 255, 0, 255), font= font)

        strongshadow= bg.filter(ImageFilter.GaussianBlur(25* scale))

        softshadow= bg.filter(ImageFilter.GaussianBlur(50* scale))
        img.paste("white", mask= softshadow)
        img.convert("RGB")
        img.paste("white", mask= strongshadow)
        img.convert("RGB")
        img.paste(bg, mask= bg)
        img.convert("RGB")

        # return the TRUE rendered ink box (accounts for the font's top/bottom
        # bearings) so callers get the real on-screen top/bottom of the number.
        # (y1-y0) is unchanged vs the old return, so text-mode callers that use
        # (y1-y0)/2 are unaffected; icon mode relies on the accurate bottom.
        ink= draw.textbbox((temperature_x, temperature_y), msg, font= font)
        return ink[0], ink[1], ink[2], ink[3]


def setup_canvas(w,h, forecast_background, bg_file, bg_map, zoom, lon, lat):
    import os

    msg=""
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
                #choose background from named structure within folder
                #the dirs are background names
                basedir= os.path.join(bg_file, forecast_background)
                if os.path.isdir(basedir):
                    image_path=choose_bg_from_folder(basedir)
                    img= Image.open(image_path)
                    msg= f"chose random background from {basedir}: {image_path}"
                else:
                    #choose random bg from folder
                    image_path = choose_bg_from_folder(bg_file)
                    img= Image.open(image_path)
                    msg= f"chose random background from {bg_file}: {image_path}"


            elif os.path.isdir(os.path.join(os.path.dirname(__file__), bg_file)):
                #choose background from named structure within folder
                #the dirs are background names
                basedir= os.path.join(os.path.join(os.path.dirname(__file__), bg_file), forecast_background)
                if os.path.isdir(basedir):
                    image_path = choose_bg_from_folder(basedir)
                    img= Image.open(image_path)
                    msg= f"chose background from named structure within folder {basedir}: {image_path}"


                else:
                    basedir= os.path.join(os.path.dirname(__file__), bg_file)
                    image_path= choose_bg_from_folder(basedir)
                    img= Image.open(image_path)
                    msg= f"chose random background from {basedir}: {image_path}"

            else:
                msg= "Can't load \n{}\n as background. Please specify a directory or filename. Try using an absolute path?".format(os.path.abspath(bg_file))

            img= remove_transparency(img)
            img= resize_fill(img, w, h) 


        elif bg_map:
            #load map image
            img= load_map(lat, lon)   
            img= resize_distort(img, w, h) 
        elif zoom:
            #load zoomed map image
            img= load_map_zoom(lat, lon, w, h)
            
        else:
            #choose from default background list
            basedir= os.path.join(os.path.dirname(__file__), 'backgrounds','default', forecast_background)
            image_path = choose_bg_from_folder(basedir)
            img= Image.open(image_path)
            img= resize_fill(img, w, h) 

    except Exception as e:
        msg= e, ": using blank background."

        #blank bg
        img= Image.new("RGB", (w, h), color=(255, 255, 255))

    return img, msg








def main(forecast_elements, 
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
    verbose,
    size= None,
    symbols= 'text'):


    import os


    # create display image

    # Set up the correct display and scaling factors
    if size:
        # explicit render size (w, h) requested on the command line
        w, h= size
        ink_black, ink_color= 1, 2
    else:
        try:
            w, h, ink_black, ink_color= setup_inky(inky_colour)
        except:
            #go_to_screen= True# ...get screen size?
            w, h, ink_black, ink_color= setup_screen()

    # The whole layout below was authored in absolute pixels for the 400x300
    # Inky wHAT. `s` scales every hard-coded font size / offset / box height /
    # blur radius so any resolution renders the SAME layout, just larger.
    # min(w/400, h/300) (contain) keeps it on-screen for any aspect ratio and
    # is exactly 1.0 at 400x300, so the Inky output is unchanged.
    s= min(w/ 400.0, h/ 300.0)

    img, msg = setup_canvas(w, h, forecast_elements["forecast_background"], bg_file, bg_map, zoom, lon, lat)
    if verbose:
        print (msg)

    #add soft white top and bottom
    softshadow= Image.new("RGBA", (w, h), color= (255, 255, 255, 255))
    draw= ImageDraw.Draw(softshadow)
    draw.rectangle((0, 10* s, w, h- 50* s), fill= (0, 0, 0, 0))

    softshadow= softshadow.filter(ImageFilter.GaussianBlur(50* s))
    img.paste("white", mask= softshadow)
    img.convert("RGB")

    draw= ImageDraw.Draw(img)


    # messages at top of screen: banner, location_banner, forecast time

    top_line= 0

    # banner
    if banner:
        img= write_in_box(img, 0, 0, w, 40* s, banner, 20* s, summary_font_loader(int(20* s)), fill= (0, 0, 0, 255), spacing= 0, align_x= "center", align_y= "top", scale= s)
        top_line+= 25* s

    # location_banner
    if location_banner:
        img= write_in_box(img, 0, top_line, w, 40* s+ top_line, location_banner, 20* s, summary_font_loader(int(20* s)), fill= (0, 0, 0, 255), spacing= 0, align_x= "center", align_y= "top", scale= s)
        top_line+= 25* s

    # forecast time
    img= write_in_box(img, 0, top_line, w, 40* s+ top_line, forecast_elements["local_now"], 70* s- top_line, summary_font_loader(int(70* s- top_line)), fill= (0, 0, 0, 255), spacing= 0, align_x= "center", align_y= "top", scale= s)


    
    # temperature in centre of screen

    #current temperature
    x0, y0, x1, y1= text_box2(img, 0, 0, w, h- 90* s, forecast_elements["temperature_msg"], int(110* s), temperature_font_loader(int(110* s)),
        fill= (255, 255, 0, 255), spacing= 0, align_x= "center", align_y= "center", scale= s)

    # top and bottom of the temperature ink — in icon mode the side blocks are
    # bottom-aligned to temp_bottom, and the RHS icon is kept below temp_top.
    temp_top= y0
    temp_bottom= y1

    # shared vertical geometry for the icon-mode side blocks: both times sit on
    # temp_bottom; the RHS icon floats up into the gap toward temp_top, and the
    # LHS top line is raised to that same height so the two blocks look balanced.
    _tf= summary_font_loader(int(24* s))
    _th= _sz(_tf, "00:00")[1]
    icon_gap= 4* s
    side_time_top= temp_bottom- _th
    icon_px= int(min(80* s, max(24* s, side_time_top- temp_top- icon_gap)))
    icon_top= max(int(temp_top), int(side_time_top- icon_gap- icon_px))

    temperature_y= (y1- y0)/ 2





    #HI/Lo on LHS MIDDLE
    temp_indicator= forecast_elements.get('temp_indicator') if symbols == 'icons' else None

    if temp_indicator:
        # icon mode (Option C): a small thermometer gauge (empty = low, full =
        # high) with its top aligned to the RHS sun/moon top, the temperature
        # right beside it, and that [thermometer + temp] group centred above the
        # time. Plain black/white by background.
        tfont= summary_font_loader(int(24* s))
        temp_str= temp_indicator['temp']
        time_str= temp_indicator['time']
        asc, desc= tfont.getmetrics()

        therm_px= int(icon_px* 0.8)             # a touch smaller than the sun/moon
        raw= load_icon(temp_indicator['icon'], therm_px)
        tw_ic= raw.width
        gap= int(6* s)
        tw_temp, th_temp= _sz(tfont, temp_str)
        tw_time= _sz(tfont, time_str)[0]

        left_x= int(5* s)
        # nudge down ~2 tick-marks so the thermometer sits level with the sun/moon
        # art (whose glyph has a little top padding inside its box)
        therm_top= icon_top+ int(therm_px* 0.12)
        temp_x= left_x+ tw_ic+ gap
        temp_baseline= int(therm_top+ therm_px/ 2+ th_temp/ 2)   # temp centred on the thermometer
        group_w= tw_ic+ gap+ tw_temp
        time_x= int(left_x+ group_w/ 2- tw_time/ 2)              # time centred under the group
        time_baseline= temp_bottom

        # plain black/white, chosen by the background (classic drop-shadow)
        if mean_of_area(img, left_x, therm_top, int(temp_x+ tw_temp), int(temp_bottom))> .5* 255:
            fill= (0, 0, 0, 255); shadowfill= (255, 255, 255)
        else:
            fill= (255, 255, 255, 255); shadowfill= (0, 0, 0)

        icon= mono_icon(raw, fill)
        bg= Image.new("RGBA", img.size, color= (0, 0, 0, 0))
        bg.paste(icon, (left_x, therm_top), icon)
        draw= ImageDraw.Draw(bg)
        draw.text((temp_x, temp_baseline), temp_str, fill= fill, font= tfont, anchor= "ls")
        draw.text((time_x, time_baseline), time_str, fill= fill, font= tfont, anchor= "ls")

        strongshadow= bg.filter(ImageFilter.GaussianBlur(25* s))
        softshadow= bg.filter(ImageFilter.GaussianBlur(50* s))
        img.paste(shadowfill, mask= softshadow)
        img.convert("RGB")
        img.paste(shadowfill, mask= strongshadow)
        img.convert("RGB")
        img.paste(bg, mask= bg)
        img.convert("RGB")

    else:
        padding= 50* s
        max_width= w- padding
        max_height= 250* s
        font_size= 24* s
        below_max_length= False
        scale_adjust= 1
        msg= forecast_elements['hi_lo_msg']

        while not below_max_length:
            summary_font= summary_font_loader(int(font_size* scale_adjust))
            reflowed= reflow_summary(msg, max_width, summary_font)
            p_w, p_h= _sz(summary_font, reflowed)  # Width and height of summary
            p_h= p_h* (reflowed.count("\n")+ 1)   # Multiply through by number of lines

            if p_h < max_height:
                below_max_length= True              # The summary fits! Break out of the loop.
            else:
                # scale down text to fit
                scale_adjust*= .95

        # x- and y-coordinates for the top left of the summary
        summary_x= 5* s   #do i need to check for the longest linw and get size of that?
        summary_y= temperature_y+ 48* s

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

        strongshadow= bg.filter(ImageFilter.GaussianBlur(25* s))

        softshadow= bg.filter(ImageFilter.GaussianBlur(50* s))
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
    max_height= 250* s
    font_size= 24* s
    below_max_length= False
    scale_adjust= 1
    msg= forecast_elements["sun_msg"]
    sun_indicator= forecast_elements.get('sun_indicator') if symbols == 'icons' else None

    if sun_indicator:
        # icon mode: a sun (coming sunrise) or the current moon phase (coming
        # sunset) above the time, right-aligned on the RHS, with a soft halo so
        # it stays legible on any background.
        # Same font/size as the hi/lo block so the two times sit level.
        time_font= summary_font_loader(int(24* s))
        t= sun_indicator['time']
        tw, th= _sz(time_font, t)
        right= w- 5* s

        # right-align the time and bottom-align its baseline to the temperature
        # bottom (matches the hi/lo block, so both lower lines are level with it)
        time_x= int(right- tw)
        time_baseline= temp_bottom
        time_top= time_baseline- th

        # icon uses the shared vertical geometry (icon_px, icon_top), centred over
        # the time — the LHS top line is raised to icon_top so the two balance.
        icon_y= icon_top
        icon_x= int(right- tw/ 2- icon_px/ 2)

        # plain black/white, chosen by the background (classic drop-shadow); the
        # icon is a solid silhouette in the same colour as the text
        if mean_of_area(img, time_x, time_top, min(time_x+ tw, w- 1), min(time_top+ th, h- 1))> .5* 255:
            fill= (0, 0, 0, 255); shadowfill= (255, 255, 255)
        else:
            fill= (255, 255, 255, 255); shadowfill= (0, 0, 0)

        icon= mono_icon(load_icon(sun_indicator['icon'], icon_px), fill)

        bg= Image.new("RGBA", img.size, color= (0, 0, 0, 0))
        bg.paste(icon, (icon_x, icon_y), icon)
        draw= ImageDraw.Draw(bg)
        draw.text((right, time_baseline), t, fill= fill, font= time_font, anchor= "rs")

        halo= bg.split()[-1].filter(ImageFilter.GaussianBlur(12* s))
        img.paste(shadowfill, mask= halo)
        img.convert("RGB")
        img.paste(bg, mask= bg)
        img.convert("RGB")

    elif msg:
        while not below_max_length:
            summary_font= summary_font_loader(int(font_size* scale_adjust))
            reflowed= reflow_summary(msg, max_width, summary_font)
            p_w, p_h= max((_sz(summary_font, line) for line in reflowed.splitlines())) # Width and height of summary
            p_h= p_h* (reflowed.count("\n")+ 1)   # Multiply through by number of lines

            if p_h < max_height:
                below_max_length= True              # The summary fits! Break out of the loop.
            else:
                # scale down text to fit
                scale_adjust*= .95

        # x and y coordinates for the top left of the summary
        summary_x= w- p_w- 5* s
        summary_y= temperature_y+ 48* s

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

        strongshadow= bg.filter(ImageFilter.GaussianBlur(25* s))
        softshadow= bg.filter(ImageFilter.GaussianBlur(50* s))


        img.paste(shadowfill, mask= softshadow)   
        img.convert("RGB")
        img.paste(shadowfill, mask= strongshadow)  
        img.convert("RGB")
        img.paste(bg, mask= bg)
        img.convert("RGB")



    

    #rain graphic and sun (UV) strength

    y0= 0
    y1= int(130* s)
    bar= 16* s               # height of the hourly UV / label row

    rain_img= Image.new("RGBA", (w, y1), color= (255, 255, 255, 0))
    draw= ImageDraw.Draw(rain_img)
    font= summary_font_loader(int(14* s))

    for i, hour in enumerate(forecast_elements["hours"]):
        p= int(forecast_elements["probOfPrecipitation"][i]* forecast_elements["precipitationRate"][i]* 255* 100) #should be x 255
        x0= int(w/ 24* i)
        x1= int(w/ 24* (i+ 1))
        pcolor= int(forecast_elements["probOfPrecipitation"][i]* 255* .5) #.5 is a fade factor - don't want bars too strong
        tcolor= 0
        if p:
            #rain_indicator
            draw.rectangle((x0, y1- bar- 3* s, x1- 1, y1- bar- 1* s), fill= (0, 0, 0, p))
            #rain bars
            draw.rectangle((x0, clamp(y0, y1- (forecast_elements["precipitationRate"][i]/ 2* (y1- y0)), y1- bar), x1- 1, y1- bar), fill= (0, 0, 0, pcolor), outline= (0, 0, 0, 255))




        #UV rectangles
        if forecast_elements["uvIndex"][i]:

            if forecast_elements["uvIndex"][i] == 1:
                uv= int(255* .025)
            elif forecast_elements["uvIndex"][i] == 2:
                uv= int(255* .05)
            elif forecast_elements["uvIndex"][i] == 3:
                uv= int(255* .075)
            else:
                uv= (forecast_elements["uvIndex"][i] > 3)* 255
            draw.rectangle((x0, y1- bar, x1- 1, y1), fill= (255, 255, 255, 255), outline= (0, 0, 0, 255))
            draw.rectangle((x0, y1- bar, x1- 1, y1), fill= (255, 255, 0, uv), outline= (0, 0, 0, 255))

        draw.text((x0+ 2* s, y0- bar+ y1), hour, fill= (0, 0, 0, 255), font= font, align= 'center') #added a plus one to look better lined up
        

        img.paste(rain_img, box= (0, h- y1), mask= rain_img)

    img.convert("RGB")




    #forecast hourly summary at bottom
    #img= write_in_box(img, 0, 280- 120, w, 270, summary, 20, summary_font_loader(20), fill= (0, 0, 0, 255), spacing= 0, align_x= "center", align_y= "bottom")


    if show_on_inky:
        #dither before saving or displaying
        img.convert("RGB")
        img= inky_dither(img)


    if save_image:
        img.convert("RGB")
        #save image
        img.save(save_image)
        if verbose:
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






