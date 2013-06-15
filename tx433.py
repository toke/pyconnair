#!/usr/bin/python

import socket
import argparse

PROTO_IDENT    = "TXP:"
PROTO_REPEAT   = 10       # Frame repeat count
PROTO_PAUSE    = 5600
PROTO_TUNE     = 350     # Time for Unit in us
PROTO_SPEED    = 16
PROTO_LOW      = 1
PROTO_HIGH     = 3

"""
EV1527, RT1527, FP1527 or HS1527
https://code.google.com/p/rc-switch/wiki/KnowHow_LineCoding
"""
codebits2 = {
    '0': (1,3),
    '1': (3,1),
    'S': (1,31)
}



class InvalidCodeBit(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class InvalidAddress(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class InvalidCommand(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)



class ProtoABC(object):

    def __init__(self, code):
        self.code    = code

    def __len__(self):
        return len(self.to_timings())

    def __str__(self):
        ','.join(self._to_timings())

    def to_timings(self):
        return list(self._to_timings())


        

class ProtoA(ProtoABC):
    """
    SC5262 / SC5272, HX2262 / HX2272, PT2262 / PT2272
    https://code.google.com/p/rc-switch/wiki/KnowHow_LineCoding
    """
    codebits = {
        '0': (1,3,1,3),
        '1': (3,1,3,1),
        'F': (1,3,3,1),
        'S': (1,31)        # Sync
    }

    def __str__(self):
        return self.code

    def _to_timings(self):
        try:
            for elem in self.code:
                for timing in ProtoA.codebits[elem]:
                    yield timing
        except KeyError as e:
            raise InvalidCodeBit(e.message)


""" UDP WireProtocol 
"""
class WireProtocolA(object):

    PROTO_IDENT    = "TXP:"
    PROTO_REPEAT   = 5       # Frame repeat count
    PROTO_REPEAT   = 10      # Frame repeat count
    PROTO_PAUSE    = 5600
    PROTO_TUNE     = 350     # Time for Unit in us
    PROTO_TAIL     = ';'
    PROTO_LOW      = 1
    PROTO_HIGH     = 3


    def baud(self):
        return len(self._telegram) / 2
    
    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        p = list(self.packet())
        header = ",".join([str(n) for n in p[0]])
        body   = ",".join([str(n) for n in p[1]])
        return "%s,%s,;" % (header, body)
   
    def switch(self, switch):
        self._telegram = self.protocol(switch.telegram())
    
    """Low level telegram support"""
    def telegram(self, data):
        self._telegram = self.protocol(data)

    def header(self):
        return self._header()

    def payload(self):
        return self._payload()

    def packet(self):
        return self._packet()

    def send(self):
        sock = socket.socket(socket.AF_INET, # Internet
                             socket.SOCK_DGRAM) # UDP
        sock.sendto(str(self), (self.ip, self.port))


class ConAir(WireProtocolA):

    def __init__(self, proto=ProtoA, ip='192.168.1.136', port=49880):
        self.protocol  = proto
        self.ip        = ip
        self.port      = port
        self._telegram = None 

    def _header(self):
        return (PROTO_IDENT + "0", 0, PROTO_REPEAT, PROTO_PAUSE, PROTO_TUNE, self.baud())

    def _payload(self):
        return self._telegram.to_timings()

    def _packet(self):
        yield self._header()
        yield self._payload()



class Intertechno(object):

    CODE = (
        '0000', 'F000', '0F00', 'FF00', '00F0', 'F0F0', '0FF0', 'FFF0',
        '000F', 'F00F', '0F0F', 'FF0F', '00FF', 'F0FF', '0FFF', 'FFFF'
    )
    COMMAND = {
        'ON':  'FF',
        'OFF': 'F0'
    }

    def __init__(self, master, slave):
        self.master = master
        self.slave  = slave
        self.addr   = Intertechno.convert_address(master, slave)

    def command(self, cmd):
        try:
            cmd = Intertechno.COMMAND[cmd]
        except KeyError as e:
            raise InvalidCommand(e.message)

        self._telegram = '%s%sS' % (self.addr, cmd)
        return self

    def on(self):
        return self.command('ON')

    def off(self):
        return self.command('OFF')
 
    def telegram(self):
        return str(self._telegram)

    def __str__(self):
        return str(self._telegram)

    @classmethod
    def convert_address(cls, master, slave):
        master_addr = ord(str(master).upper()) - 65
        slave_addr  = slave - 1
        try:
            master_b = cls.CODE[master_addr]
            slave_b  = cls.CODE[slave_addr]
        except KeyError as e:
            raise InvalidAddress(e.message)
        return "%s%s0F" % (master_b, slave_b)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--ip', help='IP-Address', type=str, default='192.168.1.136')

    parser.add_argument('address', help='address like A 1', type=str, nargs=2)
    parser.add_argument('command', help='command to execute', choices=['off', 'on'])
    args = parser.parse_args()
    
    switch =  Intertechno(args.address[0], int(args.address[1]))
    #schlafzimmer = Intertechno('J', 1)
    #box          = Intertechno('l', 8)

    p = ConAir(ip=args.ip)
    p.switch(switch.command(args.command.upper()))
    p.send()

