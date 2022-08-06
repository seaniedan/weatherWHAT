To discover weather around the world using natural text ('Paris, France'), install [geopy](https://geopy.readthedocs.io/en/stable/)
```
cd weatherWHAT
python3 -m venv venv
source venv/bin/activate
pip3 install geojson suncalc python-dateutil timezonefinder geopy
```

[Pillow, a fork of the Python Imaging Library (PIL)](https://pillow.readthedocs.io/en/stable/) is used to draw data on the images:
```
pip3 install Pillow
```

If you want to display the images on your computer, using the -d option, Pillow requires a viewer. Install [Imagemagick](https://imagemagick.org/script/download.php): 
```
sudo apt-get update && sudo apt-get install imagemagick
```
