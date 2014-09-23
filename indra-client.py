
#
#  indra client
#
# (c) 2014 ffff (http://cosmopol.is) 
# MIT license 

from entropy import compute_entropy
from mindwave_mobile import ThinkGearProtocol, ThinkGearRawWaveData, ThinkGearEEGPowerData
import json, requests; from datetime import datetime, date
import time
import dateutil.parser; import dateutil.relativedelta
import sys, platform

class Client():

    def __init__(self):
        self.username = None
        self.entropy_window = 1024
        self.raw_log = []
        self.timediff = None
	self.port = '/dev/tty.MindWaveMobile-DevA'

    # calculates the diff between our local time and the server's time
    def set_timediff(self, server_time_string):
        server_time = dateutil.parser.parse(server_time_string).replace(tzinfo=None)
        now = datetime.utcnow().replace(tzinfo=None)
        self.timediff = dateutil.relativedelta.relativedelta(now,server_time)

    def get_server_time(self):
        return datetime.utcnow().replace(tzinfo=None) + self.timediff

    def ship_biodata(self, data_type, payload):
        # handler for the date
        dthandler = lambda obj: (
            obj.isoformat()
            if isinstance(obj, datetime)
            or isinstance(obj, date)
            else None)
    # construct json
        j = json.dumps({'username':self.username,
              'time':self.get_server_time(),
           'data_type':data_type, 
           'payload':payload}, default=dthandler)
    # post json
        r = requests.post(
            'http://indra.coolworld.me',
            data=j,
            headers={'content-type': 'application/json'}
        )

    def run(self):

        # get username
        self.username = raw_input('Enter a username: ')
	
	# get port
        if 'Windows' in platform.system():
            port_number = raw_input('Windows OS detected. Please select proper COM part number:')
            port= "COM%s"%port_number if len(port_number)>0 else "COM%5"

	# prompt user to pair mindwave
        raw_input('Pair your mindwave with your laptop. Just flip the switch on the side of the device. Press ENTER when it\'s paired.')

        print '\nconnecting...',
        # set the timediff before doing anything
        self.set_timediff(
            requests.get('http://indra.coolworld.me').json()['time']
        )
        print('connected! starting to read mindwave data....') 


        for pkt in ThinkGearProtocol(self.port).get_packets():

            for d in pkt:

                if isinstance(d, ThinkGearRawWaveData): 
                    self.raw_log.append(float(str(d))) #how/can/should we cast this data beforehand?

                    # compute and ship entropy when we have > 512 raw values
                    if len(self.raw_log) > self.entropy_window:
                        entropy = compute_entropy(self.raw_log)
                        #print entropy
                        #ship_biodata('entropy',entropy)
                        self.raw_log = []

                if isinstance(d, ThinkGearEEGPowerData): 
                    # TODO: this cast is really embarrassing
                    reading = eval(str(d).replace('(','[').replace(')',']'))
                    print reading
                    self.ship_biodata('eeg_power',reading)

if __name__ == '__main__':
   client = Client()
   client.run() 
