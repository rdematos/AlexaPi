# AlexaPi with SenseHAT

---

This turns a Raspberry Pi and SenseHAT into an Alexa Voice Service (AVS) device (endpoint). Using SenseHAT, the device supports "raise to speak" and uses the builtin 8x8 LED for feedback for recording, processing, and speaking. It is based on Sam Machin AlexaPi with modifications to support SenseHAT.

### Hardware Requirements

You will need:
* Raspberry Pi and wifi dongle.
* SD Card with a fresh install of Raspbian (https://www.raspberrypi.org/downloads/raspbian/) tested against build 2015-11-21 Jessie.
* External speaker with 3.5mm Jack (http://www.amazon.com/gp/product/B001UEBN42)
* Microphone (http://www.amazon.com/gp/product/B00M3UJ42A)
* SenseHAT (http://www.amazon.com/gp/product/B014HDG74S)

![sensehatavs](https://cloud.githubusercontent.com/assets/712006/13404661/c24b9cb0-dee8-11e5-8966-3923d479a966.JPG)

### AVS Setup

Before you get started with the hardware, you will need to create device ID and keys necessary to provision and use AVS from the Raspberry Pi.
* Go to https://developer.amazon.com/edw/ and login using your amazon.com credentials.
* Once logged in, go to Alexa Voice Service (https://developer.amazon.com/edw/home.html#/avs/list)
* Register a Product type using the following information, for example:
** Company name: (you github handle)
** Device Type ID: AlexaPi
** Display Name: AlexaPi
* Create a New Security Profile and add the following web settings:
** Allowed origins: add http://IP:5000 where IP is the address used to access the provisioning service running on the Raspberry Pi.
** Return URL: add http://IP:5000/code where IP is the address used to access the provisioning service running on the Raspberry Pi.
Make a note of these credentials you will be asked for them during the install process
* Add Device details.


### Installation

Switch to root user
`sudo su`
Clone this repo to the Pi
`git clone https://github.com/rdematos/AlexaPi.git`
Run the setup script and follow its instructions.  Note that script prompts for the information from the AVS Setup and populates creds.py
`./setup.sh`

### Provisioning
Once, setup is complete you will need to provision the device for AVS. This is done by launching a provisioning service auth_web.py which accesses Login with Amazon via oAuth and returns a token for this device. This step is only needed once to retrieve the initial token. To provision:  
* run auth_web.py
* open a web browser to http://IP:5000 where IP is the address used to access the provisioning service running on the Raspberry Pi
* Login with the amazon.com account used in AVS setup; once successfully logged in, page will redirect to return URL http://IP:5000/code which displays and writes the request_token to creds.py
The auth token is generated from the request_token the auth_token is then stored in a local memcache with and expiry of just under an hour to align with the validity at Amazon, if the function fails to get an access_token from memcache it will then request a new one from Amazon using the request_token

### Usage
* Pi will use the accelerometer to trigger the recording so it is important to boot it while it is flat on the desk.
* After booting, wait for "Hello" welcome message and scrolling message "Rasie to Speak"
* Raise the Pi (pointing the USB ports up); this will start the recording and turn the LED to cyan
* Lower the Pi (flat) to stop the recording and send the audio to AVS; this will turn the LED to blue. If message is understood, AVS device will play the speech output. While it is playing, LED turns green. If message is not understood or if there was an error reaching AVS, LED will blink red three times and

### Issues/Bugs etc.

Errors are logged to /var/log/alexa.log
If the error is complaining about alsaaudio you may need to check the name of your soundcard input device, use
`arecord -L`
The device name can be set in the settings at the top of main.py
You may need to adjust the volume and/or input gain for the microphone, you can do this with
`alsamixer`








---
