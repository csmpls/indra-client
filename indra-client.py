
#
#  indra client
#
# (c) 2014 ffff (http://cosmopol.is) 
# MIT license 

from entropy import compute_entropy
from mindwave_mobile import ThinkGearProtocol, ThinkGearRawWaveData, ThinkGearEEGPowerData
import json
from socketIO_client import SocketIO


username = 'ffff'


def ship_biodata(socket, data_type, payload):
    socket.emit('biodata',
        json.dumps({'username':username,
            'data_type':data_type, 
            'payload':payload}))


def main():

    # connect to the server
    socket = SocketIO('localhost', 3000)

    raw_log = []
    #logging.basicConfig(level=logging.DEBUG)

    for pkt in ThinkGearProtocol('/dev/tty.MindWaveMobile-DevA').get_packets():

        for d in pkt:

            if isinstance(d, ThinkGearRawWaveData): 
 
                raw_log.append(float(str(d))) #how/can/should we cast this data beforehand?

                # compute and ship entropy when we have > 512 raw values
                if len(raw_log) > 256:
                    entropy = compute_entropy(raw_log)
                    print entropy
                    ship_biodata(socket,'entropy',entropy)
                    raw_log = []

            if isinstance(d, ThinkGearEEGPowerData): 
                    print d
                    ship_biodata(socket,'eeg_power',str(d))

if __name__ == '__main__':
    main()