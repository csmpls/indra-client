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
2. Change the line in `run` to `for pkt in ThinkGearProtocol('COM6').get_packets():` (thanks to [hassan](https://github.com/jannah))
3. Wear the headset and run `python indra-client.py`.
