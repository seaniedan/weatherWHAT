To get the sunrise and sunset times, weatherWHAT uses [suncalc](https://pypi.org/project/suncalc/). 
To discover weather around the world using natural text ('Paris, France'), weatherWHAT uses [geopy](https://geopy.readthedocs.io/en/stable/).
[Pillow, a fork of the Python Imaging Library (PIL)](https://pillow.readthedocs.io/en/stable/) is used to draw data on the images.

If using 'venv', set your environment:
```
source venv/bin/activate
```
The install the dependencies with
```
pip install -r requirements.txt  
```

To display the images on your computer, using the -d option, Pillow requires a viewer. Install [Imagemagick](https://imagemagick.org/script/download.php): 
```
sudo apt-get update && sudo apt-get install imagemagick
```
