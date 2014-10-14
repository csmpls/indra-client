
#
#  indra client
#
# (c) 2014 ffff (http://cosmopol.is) 
# MIT license 

from entropy import compute_entropy
from mindwave_mobile import ThinkGearProtocol, ThinkGearRawWaveData, ThinkGearEEGPowerData, ThinkGearPoorSignalData, ThinkGearAttentionData, ThinkGearMeditationData
import json, requests; from datetime import datetime, date
import time
import dateutil.parser; import dateutil.relativedelta
import sys, platform

class Client():

    def __init__(self,server_url):
        self.server_url = server_url[:-1] if server_url[-1] == '/' else server_url
        self.username = None
        self.entropy_window = 1024
        self.raw_log = []
        self.attention_esense= None
        self.meditation_esense= None 
        self.eeg_power= None 
        self.signal_quality = 0
        self.start_time = None
        self.end_time = None
        self.timediff = None
        self.port = '/dev/tty.MindWaveMobile-DevA'

    # calculates the diff between our local time and the server's time
    def set_timediff(self, time_string):
        given_time = dateutil.parser.parse(time_string).replace(tzinfo=None)
        now = datetime.utcnow().replace(tzinfo=None)
        self.timediff = dateutil.relativedelta.relativedelta(now,given_time)

    def get_server_time(self):
        return datetime.utcnow().replace(tzinfo=None) + self.timediff

    def ship_biodata(self):
        # handler for the date
        dthandler = lambda obj: (
            obj.isoformat()
            if isinstance(obj, datetime)
            or isinstance(obj, date)
            else None)
        # construct json
        j = json.dumps({'username':self.username,
            'start_time':self.start_time,
            'end_time':self.end_time,
            'signal_quality':self.signal_quality,
            'raw_values':self.raw_log, 
            'attention_esense':self.attention_esense,
            'meditation_esense':self.meditation_esense,
            'eeg_power':self.eeg_power
        }, 
    default=dthandler)

        # post json
        r = requests.post(
            self.server_url,
            data=j,
            headers={'content-type': 'application/json'}
        )

        print(r)

    def run(self):

        # get username
        self.username = raw_input('Enter a username: ')
    
        # get port
        if 'Windows' in platform.system():
            port_number = raw_input('Windows OS detected. Please select proper COM part number:')
            self.port= "COM%s"%port_number if len(port_number)>0 else "COM5"
        
        print('Using port: %s'%self.port)

        # prompt user to pair mindwave
        raw_input('Pair your mindwave with your laptop. Just flip the switch on the side of the device. Press ENTER when it\'s paired.')

        print '\nconnecting to server...'
        # set the timediff before doing anything
        self.set_timediff(
            requests.get(self.server_url + '/handshake').json()['time']
        )
        print 'connected to server! servertarting communication with device....'

        for pkt in ThinkGearProtocol(self.port).get_packets():

            for d in pkt:

                if isinstance(d, ThinkGearPoorSignalData):
                    self.signal_quality += int(str(d))
                    
                if isinstance(d, ThinkGearAttentionData):
                    self.attention_esense = int(str(d))

                if isinstance(d, ThinkGearMeditationData):
                    self.meditation_esense = int(str(d))

                if isinstance(d, ThinkGearEEGPowerData):
                    # this cast is both amazing and embarrassing
                    self.eeg_power = eval(str(d).replace('(','[').replace(')',']'))

                if isinstance(d, ThinkGearRawWaveData): 
                    # record a reading
                    # how/can/should we cast this data beforehand?
                    self.raw_log.append(float(str(d))) 

                    # record start time as the first raw reading 
                    if len(self.raw_log) == 1:
                        self.start_time = self.get_server_time()

                    # the data is all shipped here
                    if len(self.raw_log) == self.entropy_window:
                        self.end_time = self.get_server_time()
                        self.ship_biodata()
                        # reset variables
                        self.raw_log = []
                        self.signal_quality = 0


if __name__ == '__main__':
   client = Client('http://eegviz.coolworld.me')
   client.run() 
