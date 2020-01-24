[Pillow, a fork of the Python Imaging Library (PIL)](https://pillow.readthedocs.io/en/stable/) is used to draw data on the images:
```
pip3 install Pillow
```

To display the weather forecast on your Pimeroni Inky wHAT, attach the display to your Raspberry Pi or compatible device and install the drivers (this may take a while): 
```
sudo pip3 install inky
```

Additionally, to discover weather around the world using natural text ('Paris, France'), install [geopy](https://geopy.readthedocs.io/en/stable/)
```
pip3 install geopy
```
If you want to display the images on your computer, using the -d option, Pillow requires a viewer. Install [Imagemagick](https://imagemagick.org/script/download.php): 
```
sudo apt-get install imagemagick
```
