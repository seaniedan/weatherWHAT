# weatherWHAT

Weather forecast display for the Pimeroni Inky wHAT, with weather data powered by Darksky. If you don't have an Inky wHAT, you can display the weather on your desktop background or screensaver, or just as text in your terminal.

## Get Started

Download the git repo. Install the 

### Prerequisites

[Pillow, a fork of the Python Imaging Library (PIL)](https://pillow.readthedocs.io/en/stable/)
```
pip install Pillow
```

[Python API wrapper for the DarkSky by Detrous](https://github.com/Detrous/darksky)
```
pip3 install darksky_weather
```
If you intend to display the weather forecast on your Pimeroni Inky wHAT, attach the display to your Raspberry Pi or compatible device and install the drivers: 
```
sudo pip install inky
```
To discover weather around the world using natural text ('Paris, France'), install [geopy](https://geopy.readthedocs.io/en/stable/)
```
pip install geopy
```
### Install

Go to https://darksky.net/dev/register and enter your email adress and create a password for that site. The Darksky API allows 1000 free calls per day (one every few seconds). You don't need to give them any payment information.

Darksky will send you an email with an API code. Enter this code in api.txt

```
echo 1234567890abcde > api.txt
```



Example of getting some data out of the system or using it for a little demo


## Deploy

You can install on a Raspberry Pi [Raspberry  Pi](https://www.raspberrypi.org/) connected to a [Inky wHAT](https://shop.pimoroni.com/products/inky-what). 
If you don't have a suitable display, you can set this script up to, for example, change your desktop backdrop, or use the output images in your screensaver. 

## Contribute

Please send a message or pull request if you spot something that isn't clear or doesn't work. Want to help? 
* Write an installation script
* Share your icon packages - see 'how to create an icon package' below


## Author

* **[Sean Danischevsky](https://danischevsky.com)**


## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* [Pimeroni](https://shop.pimoroni.com/) for their inspiring products
* [Darksky](https://darksky.net) for hyperlocal weather data
* Olivia and Benet for cool drawings of various types of weather
