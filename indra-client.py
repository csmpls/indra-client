
#
#  indra client
#
# (c) 2014 ffff (http://cosmopol.is) 
# MIT license 

from entropy import compute_entropy
from mindwave_mobile import ThinkGearProtocol, ThinkGearRawWaveData, ThinkGearEEGPowerData
import threading
import json, requests; from datetime import datetime, date
import time
import dateutil.parser; import dateutil.relativedelta
import sys, platform, random

username = ''
entropy_window = 1024
linux_port = '/dev/tty.MindWaveMobile-DevA'
default_windows_port = '5'
use_port = linux_port
payload_maps ={'eeg_power':[
                            {'name':'delta', 'band':'(0.5 - 2.75Hz)', 'order':0},
                            {'name':'theta', 'band' : '(3.5 - 6.75Hz)', 'order':1},
                            {'name':'low-alpha', 'band' : '(7.5 - 9.25Hz)', 'order':2},
                            {'name':'high-alpha', 'band' : '(10 - 11.75Hz)', 'order':3},
                            {'name':'low-beta', 'band' : '(13 - 16.75Hz)', 'order':4},
                            {'name':'high-beta', 'band' : '(18 - 29.75Hz)', 'order':5},
                            {'name':'low-gamma', 'band' : '(31 - 39.75Hz)', 'order':6},
                            {'name':'mid-gamma', 'band' : '(41 - 49.75Hz)', 'order':7}
                            ]}

class Client(threading.Thread):

    def __init__(self, data_type='eeg_power'):
        self.STATUS_LIST = {'started':'Started', 
        'stopped':'Stopped', 
        'unavailable':'Unavailable',
        'error':''}
        threading.Thread.__init__(self)
        self.data_type = data_type
        self.process = None
        self.alive = False
        self.started = False
        self.status = self.STATUS_LIST['unavailable']
        self.username = None
        self.output_file_writer = None
        self.print_to_console = True
        self.print_output = False
        self.entropy_window = 1024
        self.raw_log = []
        self.timediff = None
        self.setDaemon(True)
        self.data=[]
        try:
            self.payload_map  =  payload_maps[data_type]
        except KeyError:
            self.payload_map = {}
            pass
        
    # calculates the diff between our local time and the server's time
    def set_timediff(self, server_time_string):
        server_time = dateutil.parser.parse(server_time_string).replace(tzinfo=None)
        now = datetime.utcnow().replace(tzinfo=None)
        self.timediff = dateutil.relativedelta.relativedelta(now,server_time)

    def get_server_time(self):
        return datetime.utcnow().replace(tzinfo=None) + self.timediff

    def ship_biodata(self, data_type, payload, post_to_server = True):
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
        if self.print_to_console:
            print j
        self.data[:0]=[j]
        if self.print_output:
            self.output_file_writer.write(j+'\n')
            self.output_file_writer.flush()
                        
    # post json
        if post_to_server:
            r = requests.post(
                'http://indra.coolworld.me',
                data=j,
                headers={'content-type': 'application/json'}
            )
        
    def get_data(self, last = 100):
        if last ==0 or len(self.data)<last:
            return self.data
        else:
            return self.data[:last]
    def is_alive(self):
        return self.alive
    
    def is_started(self):
        return self.started
    
    def get_status(self):
        return self.status
    
    def stop(self):
        print "Trying to stop thread "
        if self.process is not None:
            self.process.terminate()
            self.process = None
        self.alive = False
        self.status = self.STATUS_LIST['stopped']
        
    def run_client(self, username=None, windows_port=None, paired = False):

        # get username
        self.username = username if username else raw_input('Enter a username: ')
        if 'Windows' in platform.system():
            port_number = windows_port if windows_port \
                else raw_input('Windows OS detected. Please select proper COM part number (default is %s):'%windows_port)
            use_port= "COM%s"%port_number if len(port_number)>0 else "COM%s"%default_windows_port
        if not paired:
            raw_input('Pair your mindwave with your laptop. Just flip the switch on the side of the device. Press ENTER when it\'s paired.')

        print '\nconnecting...',
        # set the timediff before doing anything
        self.set_timediff(
            requests.get('http://indra.coolworld.me').json()['time']
        )
        print('connected! starting to read mindwave data....') 
        try:
            for pkt in ThinkGearProtocol(use_port).get_packets():

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
                        self.ship_biodata('eeg_power',reading)
        except Exception as e:
            print 'ERROR', e.strerror
            self.alive = False
            self.started = False
            self.status = str(e)
            print self.status
            pass
    def run_offline_client(self, username=None, array_size = 8,random_number_base = 1000, sleep=1, data_type = 'eeg_power'):
        self.username = username
        self.set_timediff(
            requests.get('http://indra.coolworld.me').json()['time']
        )
        print 'running offline mode'
        while True:
            entry_data=[]
            for i in range(array_size):
                entry_data.append(int(random.random() * random_number_base)+random_number_base/2)
#            time_now = datetime.now()
#            entry = {'time':str(time_now), 'values' : entry_data}

            self.ship_biodata(data_type, entry_data, post_to_server=False)
            time.sleep(sleep)
        #generate3 random data
        pass
    def get_payload_map(self):
        return self.payload_map
    
    def run(self, username=None, windows_port=None, paired = False, output_file = None, print_to_console = True, run_offline = False):
        self.started = True
        self.print_to_console = print_to_console
        print "Starting " + self.name
        #self.mwc_started = True
        self.alive = True
        self.status = self.STATUS_LIST['started']
        
        if output_file:
            self.output_file = output_file
            self.print_output = True
            self.output_file_writer = open(output_file, 'w')
        #store the client as a process that could be killed
        self.process = self.run_client(username, windows_port, paired) if not run_offline \
            else self.run_offline_client(username)
    
    def dump_data(self, dumpfile):
        if dumpfile:
            with open(dumpfile, 'w') as f:
                f.write(str(self.data))
                f.flush()
                f.close()

if __name__ == '__main__':
    output_file = None
    if len(sys.argv)>1:
        output_file = sys.argv[1]
        print 'printing output to %s' % output_file
        
    client = Client()
    client.run(output_file = output_file ) 

