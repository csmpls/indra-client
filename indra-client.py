
#
#  indra client
#
# (c) 2014 ffff (http://cosmopol.is) 
# MIT license 

from entropy import compute_entropy
from mindwave_mobile import ThinkGearProtocol, ThinkGearRawWaveData, ThinkGearEEGPowerData, ThinkGearPoorSignalData
import json, requests; from datetime import datetime, date
import time
import dateutil.parser; import dateutil.relativedelta
import sys, platform, random

class Client():

    def __init__(self):
        self.username = None
        self.output_file_writer = None
        self.print_to_console = True
        self.print_output = False
        self.entropy_window = 1024
        self.raw_log = []
	self.start_time = None
	self.end_time = None
	self.signal_quality = 0
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
	      'raw_values':self.raw_log}, 
	default=dthandler)

    	# post json
        r = requests.post(
            'http://indra.coolworld.me',
            data=j,
            headers={'content-type': 'application/json'}
        )

	print('.')

    def run(self):

        # get username
        self.username = raw_input('Enter a username: ')
	
	# get port
        if 'Windows' in platform.system():
            port_number = raw_input('Windows OS detected. Please select proper COM part number:')
            port= "COM%s"%port_number if len(port_number)>0 else "COM%5"

	# prompt user to pair mindwave
        raw_input('Pair your mindwave with your laptop. Just flip the switch on the side of the device. Press ENTER when it\'s paired.')

        print '\nconnecting to server...'
        # set the timediff before doing anything
        self.set_timediff(
            requests.get('http://indra.coolworld.me').json()['time']
        )
        print 'connected! when you see periods being printed, data is being shipped to the server. thanks for participating.'


        for pkt in ThinkGearProtocol(self.port).get_packets():

            for d in pkt:

		if isinstance(d, ThinkGearPoorSignalData):
		    self.signal_quality += int(str(d))
		    

                if isinstance(d, ThinkGearRawWaveData): 

		    #how/can/should we cast this data beforehand?
                    self.raw_log.append(float(str(d))) 

		    if len(self.raw_log) == 1:
		        self.start_time = self.get_server_time()

		    if len(self.raw_log) == self.entropy_window:
		        self.end_time = self.get_server_time()
                        self.ship_biodata()
		        # reset variables
                        self.raw_log = []
		        self.signal_quality = 0



if __name__ == '__main__':
   client = Client()
   client.run() 
