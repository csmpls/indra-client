
#
#  indra stress tester
#
# (c) 2014 ffff (http://cosmopol.is) 
# MIT license 

import json, time, random,sys
from socketIO_client import SocketIO


def ship_biodata(socket, username, data_type, payload):
    socket.emit('biodata',
        json.dumps({'username':username,
            'data_type':data_type, 
            'payload':payload}))

def main(username):

    print username

    # connect to the server
    socket = SocketIO('http://indra.coolworld.me')

    num_entropy = 0
    num_power = 0

    random.seed()

    while True:
    
        time.sleep(0.5) 
        ship_biodata(socket,username,'entropy',random.random()*2 -1 )
        num_entropy+=1

        time.sleep(0.5) 
        ship_biodata(socket,username,'entropy',random.random()*2 -1 )
        num_entropy+=1
        reading = [random.randint(0,3000) for x in range(7)] 
        ship_biodata(socket,username,'eeg_power',reading)
        num_power+=1

        print num_entropy, num_power

if __name__ == '__main__':
    main(sys.argv[1])
