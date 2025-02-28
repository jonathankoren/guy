# Guy -- A Digital Companion

## License
Software are copyright Jonathan Koren, 2025.

Software is licensed under the Gnu Public License V3 (GPLv3).

STL files are public domain.

## About / How To Use
This project turns an abandonded Yeti Blue microphone stand into nifty
anthropomorphic data display art piece.

Guy is capable of displaying information from any number of sources including
WeeWx weather and Open Sky.
(*This list is incomplete; you can help by expanding it.*)

Tapping on the sides of the display switches between the different modes, while
tapping in the middle performs some action specific to the current mode.

Please note, that at least one second must pass between taps.

**WARNING! This code is -- and probably forever will be -- hackerware.**


## Hardware
### Recommended Electronic Components
* [Round RGB 666 TTL TFT Display - 2.1" 480x480 - Capacitive Touch - TL021WVC02CT-B1323 PID: 5792](https://www.adafruit.com/product/5792)
* [Adafruit Qualia ESP32-S3 for TTL RGB-666 Displays PID: 5800](https://www.adafruit.com/product/5800)
* USB-C cable

### Nonprintable Components
* The microphone desk stand for a Blue Yeti microphone
* Optional: Two M3 x 6 mm x 5 mm threaded heat inset
* Optional: Two M3 x 6 mm grub screws

### Printable Components
The face is printed in four files: `back`, `internal`, `face`, and `clip`.
Orient the models appropriately and supports are not required.
*The STLs do not come in the proper orientation.* It is strong recommended that
the clip is oriented on its side so that the print layers run vertically when
placed on the microphone stand.

If desired, you can print the `screwed-face` and `screwed-back` files. These
can accept M3 threaded heat inserts and M3 grub screws to more securely fasten
the face plate to the back. In my experience, a friction fit is strong enough.

## Software Installation
1. Edit the settings.toml.example to contain values appropriate to your setting.
By default this would be Wifi SSID and password, along with a URL to for
fetching weather data, and the latitude-longitude bounding box for fetching
ADS-B flight tracking data.

2. If you are *not* using a Adafruit Round RGB 666 TTL TFT Display - 2.1 inch display, then you will need to modify `code.py` to use the appropriate driver.
find the line `graphics = Graphics(Displays.ROUND21, ...` and replace the
constant `Displays.ROUND21` with whatever is appropriate.

3. If you change the modules from the default `Weather` and `OpenSky` modules
then you will also need to edit the `modules = [ Weather(os.getenv( ...)` line
to use whatever modules you wish to use.

4. Copy the files over to your CircuitPython device, and then reboot the device.

## Hardware Construction
1. Attach the display to the Qualia ESP32

2. Place the Qualia ESP32 face down in the `back` so oriented so that the USB-C
port is aligned with the notch. Note that the chips will be pointed down and
the screen printed Adafruit logo will be pointed up.

3. Place the `internal` stand on top of the circuit board. You may secure it
to the board with some screws, but it is not required.

4. Fold the display over so that screen is pointing up.

5. Place the `face` plate on and orient it so that the notches are aligned and
the USB-C port is accessable. If you're using the grub screws, you may now
attach them.

6. Attach the USB-C cable and install the software.
*Leave Guy on for the next steps.*

7. Put the clip on the microphone stand.

8. Using a glue appropriate for your printing material (e.g. cyanoacrylate
(e.g. super glue) for PLA), place some drops into the curved part of the clip
and attach the head, making sure that both the cable is accessable and the
face is properly oriented.

## Software Description
### Requirements
Circuit Python 9 (Comes preloaded on the Adafruit Qualia ESP32.)

Additionally the following packages should be installed in the `lib/`
subdirectory on the the ESP32:
* adafruit_display_shapes
* adafruit_bitmap_font
* adafruit_display_text
* adafruit_qualia
* adafruit_requests

These packages are available from https://github.com/adafruit and
http://adafruit.com .

### code.py
This is the main function. It sets up the hardware and handles the touch events.
This file will need to be modified if different modules or displays are used.

### Weather
Fetches current weather data from a [WeeWx](https://weewx.com/) weather station
and displays it as a Chernoff face. Technically, it can work with any data
source, provided it conforms the to included `weather-example.json`. Tapping
the middle of display toggles between the face and text display.

The Chernoff face changes depending on the weather.
| Facial Feature  | Weather Feature |
| --------------- | --------------- |
| Eyebrows        | Wind            |
| Eyes            | Humidity        |
| Nose            | Temperature     |
| Mouth           | Air quality     |
| Color           | Air quality     |

Providing additional data sources is left as an exercise for the reader.

### OpenSky
Displays the location of aircraft currently flying in a region based on ADS-B
data available from Open Sky. Tapping on the display does nothing.

### FaceAnimation
Displays various faces. Tapping on the display changes the color.

## Developing Your Own Modules
Modules are simply Python classes that implement the following functions:
```
class MyModule:
  def draw(self, timestamp):
    '''Called whenever the display needs updated. Returns a pair containing
    the number of seconds the display is valid for and a displayio drawing group
    containing what should be displayed on the screen.'''
    return (ttl, displayio_group)

  def tap(self, x, y):
    '''Like draw(), but called whenever the screen is tapped.'''
    return (ttl, displayio_group)
```

You can then add your class to the list of modules inside `code.py`.
