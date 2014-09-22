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
2. Go to “Devices and Printers”. Right-click on the MindWave device icon and selected “Properties”. In this dialog there is a tab “Hardware” under which the port name of your MindWave is displayed.
3. Change the line in `run` to `for pkt in ThinkGearProtocol('COM#').get_packets():`, where `#` is the name of the COM port you found. (thanks to [linda bäbler](twitter.com/baeblerl))
4. Wear the headset and run `python indra-client.py`.
