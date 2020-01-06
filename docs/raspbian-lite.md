If you don't have pip3 (for example if using raspbian-lite), you'll first need to install it:
```
sudo apt-get update
sudo apt install python3-pip
```
The [Python API wrapper for DarkSky by Detrous](https://github.com/Detrous/darksky) is used to parse the weather information:
```
pip3 install darksky_weather
```

[Pillow, a fork of the Python Imaging Library (PIL)](https://pillow.readthedocs.io/en/stable/) is used to draw data on the images:
```
pip3 install Pillow
```

To display the weather forecast on your Pimeroni Inky wHAT, attach the display to your Raspberry Pi or compatible device and install the drivers (this may take a while): 
```
sudo pip3 install inky
```
