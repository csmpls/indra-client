import entropy
import mindwave-mobile as mw


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
                    ent = entropy.compute_entropy(raw_log)
                    print ent
                    raw_log = []


if __name__ == '__main__':
    main()