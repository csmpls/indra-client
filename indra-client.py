
#
#  indra client
#
# (c) 2014 ffff (http://cosmopol.is) 
# MIT license 

from entropy import compute_entropy
from mindwave_mobile import ThinkGearProtocol, ThinkGearRawWaveData
import json
from socketIO_client import SocketIO

username = 'ffff'

def main():

    # connect to the server
    socket = SocketIO('localhost', 3000)

    raw_log = []
    #logging.basicConfig(level=logging.DEBUG)

    for pkt in ThinkGearProtocol('/dev/tty.MindWaveMobile-DevA').get_packets():

        for d in pkt:

            # compute entropy
            if isinstance(d, ThinkGearRawWaveData): 
                raw_log.append(float(str(d))) #how/can/should we cast this data beforehand?
                if len(raw_log) > 512:
                    entropy = compute_entropy(raw_log)
                    print entropy
                    ship_data(socket,'entropy',entropy)
                    raw_log = []

def ship_data(socket, biodata_type, payload):
    socket.emit('biodata',
        json.dumps({'username':username,
            'biodata_type':biodata_type, 
            'payload':payload}))

if __name__ == '__main__':
    main()