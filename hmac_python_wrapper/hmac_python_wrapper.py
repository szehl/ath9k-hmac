import sys
import datetime
import time
import inspect
import subprocess
import zmq


"""
A hybrid TDMA CSMA MAC based on Atheros and ath9k wifi driver
"""
class HybridTDMACSMAMac():
    def __init__(self, no_slots_in_superframe, slot_duration_ns):
        #super(HybridTDMACSMAMac,self).__init__()
        self.name = "hybridTDMACSMA"
        self.desc = "works w/ ath9k"
        self.mNo_slots_in_superframe = no_slots_in_superframe
        self.mSlot_duration_ns = slot_duration_ns
        self.acs = []
        for ii in range(no_slots_in_superframe):
            self.acs.append(None)

    def getNumSlots(self):
        return self.mNo_slots_in_superframe

    def addAccessPolicy(self, slot_nr, ac):
        self.acs[slot_nr] = ac

    def getAccessPolicy(self, slot_nr):
        return self.acs[slot_nr]

    def getSlotDuration(self):
        return self.mSlot_duration_ns

    def printConfiguration(self):
        s = '['
        for ii in range(self.getNumSlots()):
            s = s + str(ii) + ': ' + self.getAccessPolicy(ii).printConfiguration() + "\n"
        s = s + ']'
        return s

    def install_mac_processor(self, interface, hybridMac):

        print 'Function: installMacProcessor'
        #self.log.info('margs = %s' % str(myargs))

       # hybridMac = pickle.loads(mac_profile)

        conf_str = None
        for ii in range(hybridMac.getNumSlots()): # for each slot
            ac = hybridMac.getAccessPolicy(ii)
            entries = ac.getEntries()

            for ll in range(len(entries)):
                entry = entries[ll]

                # slot_id, mac_addr, tid_mask
                if conf_str is None:
                    conf_str = str(ii) + "," + str(entry[0]) + "," + str(entry[1])
                else:
                    conf_str = conf_str + "#" + str(ii) + "," + str(entry[0]) + "," + str(entry[1])

        # set-up executable here. note: it is platform-dependent

        #exec_file = str(os.path.join(self.get_platform_path_hybrid_MAC())) + '/hybrid_tdma_csma_mac'
        exec_file = 'hmac_userspace_daemon/hmac_userspace_daemon'
        processArgs = str(exec_file) + " -d 0 " + " -i" +str(interface) + " -f" + str(hybridMac.getSlotDuration()) + " -n" + str(hybridMac.getNumSlots()) + " -c" + conf_str
        print 'Calling hybrid mac executable w/ = ' + str(processArgs)

        try:
            # run as background process
            subprocess.Popen(processArgs.split(), shell=False)
            return True
        except Exception as e:
            fname = inspect.currentframe().f_code.co_name
            print "An error occurred in " +str(fname) + " : " +str(e)

    def update_mac_processor(self, interface, hybridMac):

        print 'Function: updateMacProcessor'

        #hybridMac = pickle.loads(mac_profile)

        # generate configuration string
        conf_str = None
        for ii in range(hybridMac.getNumSlots()): # for each slot
            ac = hybridMac.getAccessPolicy(ii)
            entries = ac.getEntries()

            for ll in range(len(entries)):
                entry = entries[ll]

                # slot_id, mac_addr, tid_mask
                if conf_str is None:
                    conf_str = str(ii) + "," + str(entry[0]) + "," + str(entry[1])
                else:
                    conf_str = conf_str + "#" + str(ii) + "," + str(entry[0]) + "," + str(entry[1])

        #  update MAC processor configuration
        try:
            # todo cache sockets!!!
            context = zmq.Context()
            socket = context.socket(zmq.REQ)
            socket.connect("tcp://localhost:" + str("1217"))

            socket.send(conf_str)
            message = socket.recv()
            print "Received reply from HMAC: " + str(message)
            return True
        except zmq.ZMQError as e:
            fname = inspect.currentframe().f_code.co_name
            print "An error occurred in " +str(fname) + " : " +str(e)


    def uninstall_mac_processor(self, interface, hybridMac):

        print 'Function: uninstallMacProcessor'

        #hybridMac = pickle.loads(mac_profile)

        # set allow all
        # generate configuration string
        conf_str = None
        for ii in range(hybridMac.getNumSlots()): # for each slot
            # slot_id, mac_addr, tid_mask
            if conf_str is None:
                conf_str = str(ii) + "," + 'FF:FF:FF:FF:FF:FF' + "," + str(255)
            else:
                conf_str = conf_str + "#" + str(ii) + "," + 'FF:FF:FF:FF:FF:FF' + "," + str(255)

        # command string
        terminate_str = 'TERMINATE'

        #  update MAC processor configuration
        try:
            # todo cache sockets!!!
            context = zmq.Context()
            socket = context.socket(zmq.REQ)
            socket.connect("tcp://localhost:" + str("1217"))
            #socket.connect("ipc:///tmp/localmacprocessor")

            # (1) set new config
            socket.send(conf_str)
            message = socket.recv()
            print "Received reply from HMAC: " + str(message)

            # give one second to settle down
            time.sleep(1)


            # (2) terminate MAC
            socket.send(terminate_str)
            message = socket.recv()
            print "Received reply from HMAC:  " +str(message)

            return True
        except zmq.ZMQError as e:
            fname = inspect.currentframe().f_code.co_name
            print "An error occurred in " +str(fname) + " : " +str(e)

"""
AccessPolicy for each slot
"""
class AccessPolicy(object):

    def __init__(self):
        self.entries = []

    def disableAll(self):
        self.entries = []

    def allowAll(self):
        self.entries = []
        self.entries.append(('FF:FF:FF:FF:FF:FF', 255))

    def addDestMacAndTosValues(self, dstHwAddr, *tosArgs):
        """add destination mac address and list of ToS fields
        :param dstHwAddr: destination mac address
        :param tosArgs: list of ToS values to be allowed here
        """
        tid_map = 0
        for ii in range(len(tosArgs)):
            # convert ToS into tid
            tos = tosArgs[ii]
            skb_prio = tos & 30 >> 1
            tid =skb_prio & 7
            tid_map = tid_map | 2**tid

        self.entries.append((dstHwAddr, tid_map))

    def getEntries(self):
        return self.entries

    def printConfiguration(self):
        s = ''
        for ii in range(len(self.entries)):
            s = str(self.entries[ii][0]) + "/" + str(self.entries[ii][1]) + "," + s
        return s





if __name__ == "__main__":

    # hybrid MAC parameter
    dstHWAddr = "34:13:e8:24:77:be" #node on which scheme should be applied, e.g. nuc15 interface sta1
    total_slots = 10
    slot_duration = 20000
    iface = 'wlan0'

    # create new MAC for local node
    mac = HybridTDMACSMAMac(no_slots_in_superframe=total_slots, slot_duration_ns=slot_duration)

    be_slots = [1,2,3,4]

    # assign access policies to each slot in superframe
    for slot_nr in range(total_slots):
        if slot_nr in be_slots:
            acBE = AccessPolicy()
            acBE.addDestMacAndTosValues(dstHWAddr, 0)
            mac.addAccessPolicy(slot_nr, acBE)
        else:
            acGuard = AccessPolicy()
            acGuard.disableAll() # guard slot
            mac.addAccessPolicy(slot_nr, acGuard)

    # install MAC Processor
    if mac.install_mac_processor(iface, mac):
        print str(mac.printConfiguration())


    time.sleep(10)

    print "\nUpdating Hybrid MAC:"

    mac = HybridTDMACSMAMac(no_slots_in_superframe=total_slots, slot_duration_ns=slot_duration)

    be_slots = [5,6,7,8]

    # assign access policies to each slot in superframe
    for slot_nr in range(total_slots):
        if slot_nr in be_slots:
            acBE = AccessPolicy()
            acBE.addDestMacAndTosValues(dstHWAddr, 0)
            mac.addAccessPolicy(slot_nr, acBE)
        else:
            acGuard = AccessPolicy()
            acGuard.disableAll() # guard slot
            mac.addAccessPolicy(slot_nr, acGuard)

    if mac.update_mac_processor(iface, mac):
        print str(mac.printConfiguration())
         

    time.sleep(15)

    print "\nStopping Hybrid MAC:"

    if mac.uninstall_mac_processor(iface, mac):
        print str(mac.printConfiguration())

