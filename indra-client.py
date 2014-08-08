
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
entropy_window = 1024


def ship_biodata(socket, data_type, payload):
    socket.emit('biodata',
        json.dumps({'username':username,
            'data_type':data_type, 
            'payload':payload}))

class Client():

    def __init__(self):
        self.entropy_window = 1024
        self.raw_log = []

    # here is where we configure environment variables based on the server's prefernece
    def on_welcome(self, *args):
        self.entropy_window = args[0][u'entropy_window']

    def run(self):

        # connect to the server
        socket = SocketIO('http://indra.coolworld.me')
        socket.on('welcome', self.on_welcome)
        socket.wait(seconds=1)
        print 'entropy window', self.entropy_window

        #logging.basicConfig(level=logging.DEBUG)
        for pkt in ThinkGearProtocol('/dev/tty.MindWaveMobile-DevA').get_packets():

            for d in pkt:

                if isinstance(d, ThinkGearRawWaveData): 
     
                    self.raw_log.append(float(str(d))) #how/can/should we cast this data beforehand?

                    # compute and ship entropy when we have > 512 raw values
                    if len(self.raw_log) > self.entropy_window:
                        entropy = compute_entropy(self.raw_log)
                        print entropy
                        ship_biodata(socket,'entropy',entropy)
                        self.raw_log = []

                if isinstance(d, ThinkGearEEGPowerData): 
                        # TODO: this cast is really embarrassing
                        reading = eval(str(d).replace('(','[').replace(')',']'))
                        print reading
                        ship_biodata(socket,'eeg_power',reading)

if __name__ == '__main__':
   client = Client()
   client.run() 