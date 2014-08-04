# (c) 2014 ffff (http://cosmopol.is) 
# MIT license 

from entropy import compute_entropy
import mindwave-mobile as mw

# TODO: package a json with user id and payload (e.g., type:entropy)

def main():

    raw_log = []
    ent = 0
    #logging.basicConfig(level=logging.DEBUG)

    for pkt in mw.ThinkGearProtocol('/dev/tty.MindWaveMobile-DevA').get_packets():

        for d in pkt:

            # compute entropy
            if isinstance(d, mw.ThinkGearRawWaveData): 
                raw_log.append(d)
                if len(raw_log) > 512:
                    ent = compute_entropy(raw_log)
                    print ent # TODO: ship entropy value to server
                    raw_log = []

            # TODO: EEG_POWER business


if __name__ == '__main__':
    main()