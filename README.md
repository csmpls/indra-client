indra-client
============

indranet client

## setup instructions

### installing libraries

0. make sure you've installed both python and [pip](https://pypi.python.org/pypi/pip)
1. `pip install pyserial`
2. `pip install socketIO_client`

### OSX / Linux

1. Pair your MindWave Mobile with your computer via the OS.
2. When everything's paired, turn on the MindWave and make sure the light is flashing blue.
3. Wear the headset and run `python indra-client.py`.

### Windows
1. Follow steps 1-3 above.
2. Follow the instructions [here](http://plugable.com/2011/07/04/how-to-change-the-com-port-for-a-usb-serial-adapter-on-windows-7) to find the COM port for the MindWave Mobile *(TODO: figure out what this COM port is on win? I don't have a win comp so I can't do this and others online seem to be on OS X/Linux as well)*
3. Find the line containing `'/dev/tty.MindWaveMobile-DevA'` and change that bit to `'[com port you found]'`
4. Wear the headset and run `python indra-client.py`. If it starts printing numbers, you're up and running!
