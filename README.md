# SMMPix
Image comment drawing bot for Mario Maker 2

Required Hardware
=================

- A [Teensy LC](https://www.pjrc.com/teensy/teensyLC.html). A Teensy 3.x should also work, but I've only tested on the LC. The 2.0 and 2.0++ won't work.

- A [Magic NS](https://www.amazon.com/Mayflash-Magic-NS-Wireless-Controller-Nintendo/dp/B079B5KHWQ/ref=sr_1_1).

- A standard [USB to Micro B cable](https://www.amazon.com/AmazonBasics-Double-Braided-Nylon-Charger/dp/B074VM7J6B/ref=sr_1_1) (typical charging cable for Android phones)

- Any controller that plugs into the Magic NS (there's a lot of them)

- A Nintendo Switch with Mario Maker 2 (duh)

Required Software
==============

- [Arduino IDE](https://www.arduino.cc/en/main/software)

- [Teensyduino Plugin](https://www.pjrc.com/teensy/td_download.html) for Arduino IDE

- [Teensy XInput USB Mode](https://github.com/dmadison/ArduinoXInput_Teensy)

- [Python 2.7](https://www.python.org/downloads/release/python-2716/)

- [Pillow](https://pillow.readthedocs.io/en/stable/installation.html#basic-installation) (or PIL)

Usage
=====

- Create a 320 x 180 png file using your favourite image editing software. Call it (for example) `my_image.png`. Drop it in the root folder of this project.

- Open a command line in the same folder and run `python encode.py my_image.png`. This prepares the image data for upload and produces another image `my_image_dithered.png` which is a preview of what the image will look like in Mario Maker.

- Open `teensy/teensy.ino` in the Arduino IDE

- Select Tools > Board > Teensy LC

- Select Tools > USB Type > XInput

- If this isn't your first time uploading an image and the Teensy Loader is already open, close it or turn off automatic mode (automatic mode doesn't work with XInput mode).

- Connect your Teensy to your computer.

- Press the button on your Teensy.

- Click the Upload button and wait for it to compile and upload.

- If your Magic NS hasn't been set up with your Switch, follow the instructions it came with. Plug in any controller into it and follow the prompt to press L + R or whatever it asks. As long as the Magic NS stays plugged in to your Switch, you won't have to go through this flow again (even with nothing plugged into the Magic NS).

- In Super Mario Maker 2, navigate to the comment drawing screen. Place the cursor in the top left corner, with the smallest brush, with black selected.

- Plug your Teensy into your Magic NS and wait.