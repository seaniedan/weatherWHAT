# weatherWHAT

Weather forecast display for the Pimeroni Inky wHAT, with weather data powered by Dark Sky. If you don't have an Inky wHAT, you can display the weather on your desktop background or screensaver, or just as text in your terminal.

![display example](./docs/images/color_moon.png)

## Get Started

Download the git repo:
```
sudo apt install git
git clone --depth=1 https://github.com/seaniedan/weatherWHAT.git
```

### Prerequisites

If you are using Raspbian-lite, [install pip3.](./docs/raspbian-lite.md)

The [Python API wrapper for Dark Sky by Detrous](https://github.com/Detrous/darksky) is used to parse the weather information:
```
pip3 install darksky_weather
```

If you have one, [install, connect and test your Inky wHAT.](https://github.com/pimoroni/inky)

If you want to show images, and use the location functions, install [the rest of the prerequisites.](./docs/prerequisites.md)

You can also [install the additional prerequisites using Anaconda.](./docs/anacondaInstall.md)

### Install

[Register with Dark Sky](https://darksky.net/dev/register), enter your email adress and create a password. The Dark Sky API allows 1000 free calls per day and you don't need to give any payment information. 

Dark Sky will send you an email with an API code. Enter this code in api.txt by replacing the path below and using the API code they sent instead of the dummy code below (keep the quotes):
```
cd /path/to/weatherhWHAT/
echo '1234567890abcde' > api.txt
```

## Deploy

To show the weather on the command line:
```
./weatherWHAT.py
```

If you have installed the prerequisites to display an image:
```
./weatherWHAT.py -d
```

The numbers at the bpottom of the screen are hours: yellow means sunshine (high UV). Bars appearing above the numbers show the amount of rain at that hour.

If you have installed GeoPy, to see the weather in Paris:
```
./weatherWHAT.py -l 'paris, france' 
```

To display a map, use -m (or -z for the zoomed map):
```
./weatherWHAT.py -dz -l melbourne
```

To display a particular image or folder of images, use the -bg option. You'll also need -d to display the image onscreen, or -i to send to the InkyWHAT.
```
./weatherWHAT.py -bg icons/kids -d
```

Use the -h option for help!


You can use a [Raspberry Pi](https://www.raspberrypi.org/) connected to a [Inky wHAT](https://shop.pimoroni.com/products/inky-what). 
If you don't have a suitable display, you can set this script up to, for example, change your desktop backdrop, or use the output images in your screensaver. 

Use the -s option and specify a file to save to (.jpg or .png). 

e.g. On Ubuntu Mate, to update your desktop background, you can use the instructions in this file:
```
crontab examples/mate_desktop_cron.txt
```
to save the image in your desktop background location.

## Contribute

Please send a message or pull request if something isn't clear or doesn't work. 

Want to help? 
* Write an installation script.
* Share ideas, and folders of background images.
* Rewrite it to work on different resolution screens.
* Share your icon packages - see 'how to create an icon package' below.


## Author

* **[Sean Danischevsky](https://www.danischevsky.com)**


## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* [Raspberry Pi](https://www.raspberrypi.org) for a great device
* [Pimeroni](https://shop.pimoroni.com) for their inspiring products
* [Dark Sky](https://darksky.net) for hyperlocal weather data
* Lee at 90 Degrees Picture Framing, 124 Fortess Rd, London NW5 2HP (+44 20 7267 4121) for the super frame
* Olivia and Benet for cool drawings of various types of weather
