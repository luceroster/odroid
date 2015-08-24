import sys
import os
import struct
from ctypes import (CDLL, get_errno)
from ctypes.util import find_library
from socket import (
    socket,
    AF_BLUETOOTH,
    SOCK_RAW,
    BTPROTO_HCI,
    SOL_HCI,
    HCI_FILTER,
)

#~ if not os.geteuid() == 0:
    #~ sys.exit("script only works as root")

btlib = find_library("bluetooth")
if not btlib:
    raise Exception(
        "Can't find required bluetooth libraries"
        " (need to install bluez)"
    )
bluez = CDLL(btlib, use_errno=True)

dev_id = bluez.hci_get_route(None)

print("dev_id",dev_id)

sock = socket(AF_BLUETOOTH, SOCK_RAW, BTPROTO_HCI)
sock.bind((dev_id,))

#~ err = bluez.hci_le_set_scan_parameters(sock.fileno(), 0, 0x10, 0x10, 0, 0, 1000);
#~ if err < 0:
    #~ raise Exception("Set scan parameters failed")
    # occurs when scanning is still enabled from previous call

# allows LE advertising events
hci_filter = struct.pack(
    "<IQH", 
    0x00000010, 
    0x4000000000000000, 
    0
)
sock.setsockopt(SOL_HCI, HCI_FILTER, hci_filter)

err = bluez.hci_le_set_scan_enable(
    sock.fileno(),
    1,  # 1 - turn on;  0 - turn off
    0, # 0-filtering disabled, 1-filter out duplicates
    10000  # timeout
)
if err < 0:
    errnum = get_errno()
    raise Exception("{} {}".format(
        errno.errorcode[errnum],
        os.strerror(errnum)
    ))


from math import pow
def calculate_distance(p):
	p0=-59
	d0=1.0
	n=2
	d = d0*pow(10,(p0+p)/(10*n))
	return d

values=[]
while True:
    data = sock.recv(1024)
    values.append(256-data[-1])
    if len(values)>30:values.pop(0)
    p_prom=sum(values)/len(values)
    d=calculate_distance(p_prom)
    print("RSSI: %3.1f prom:%3.1f distancia: %3.1f"%(values[-1],p_prom,d))
    
    # print bluetooth address from LE Advert. packet
    #~ print(':'.join("{0:02x}".format(x) for x in data[12:6:-1])) 
    #~ print(data[12:6:-1])
    #~ print(data[::])
