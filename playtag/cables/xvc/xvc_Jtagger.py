import itertools
import pprint
import StringIO
from io import BytesIO
from ...iotemplate.stringconvert import TemplateStrings
from ctypes import c_ulonglong, byref
import socket
from itertools import izip
import binascii
import sys

def showdevs():
    print("showdevs xvc call")

def debug_dump(f, title, data, numbytes):
    print >> f, title,
    for i in range(numbytes):
        print >> f, '%02x' % ((data[i/8] >> ((i % 8) * 8)) & 0xFF),
    print >> f

class Jtagger(TemplateStrings.mix_me_in()):
    maxbits=22987852800
    chunksize=1024
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self, devname, maxbits=2**22):
	print("xvc __init__ call")
        #create an INET, STREAMing socket
        #self.s.connect(("sbc-tbed-ftk-05", 2543))
        #self.s.connect(("pc-tbed-pub-05", 2543))
        self.s.connect(("134.158.155.242", 2542))
        data = StringIO.StringIO() 
        data.write(b"shift:")
        numbits = 8
	numbytes = 1
        value0 = numbits & 0xFF
        value1 = (numbits >> 8) & 0xFF
        value2 = (numbits >> 16) & 0xFF
        value3 = (numbits >> 24) & 0xFF
        data.write("%c%c%c%c"%(value0, value1, value2, value3))
        for i in range(0, numbytes):
            value = 0xFF
            data.write("%c"%value)

        for i in range(0,numbytes):
            value = 0x55
            data.write("%c"%value)

        self.s.send(data.getvalue())
        out_data = StringIO.StringIO() 
        tdo_fromXVC = self.s.recv(numbytes)

    def __call__(self, tms, tdi, usetdo, formatter = '{0:064b}'.format, int=int, len=len):
        '''  Passed tms, tdi.  Returns tdo.
             All these are strings of '0' and '1'.
             First bit sent is the last bit in the string...

             XVC protocol foundamental command
             
             shift:<numbits><((numbits+7)/8)*2-byte vector>

             Takes as input tms and tdi vectors
             Feed them to the XVC server using XVC protocol
             Retrieves TDO output vector and put it (where??)
        '''
	print("xvc __call__ call")
	tdi = tdi[::-1]
	tms = tms[::-1]
        #print 'TDI',
        #pprint.pprint(tdi)
	#print 'TMS',
        #pprint.pprint(tms)
        numbits = len(tms)
        if not numbits:
            return
        assert 0 < numbits == len(tdi) <= self.maxbits

        numints = (numbits + 63) / 64
        leftpad = numints * 64 - numbits
        numbytes = (numbits + 7 ) / 8
        leftpad = numbytes * 8 - numbits
        print 'numbits = ',numbits
        #print 'numbytes = ',numbytes
        #print 'leftpad = ',leftpad

        #allbits = [leftpad * 2 * '0']
        #extend = allbits.extend
        # izip('ABCD', 'xy') --> Ax By
        #for x in izip(tms, tdi):
        #    extend(x)
        #allbits = ''.join(allbits) # Concatenate all allbits items using '' (nothing) as separator
        #print "allbits:",allbits
        #print "len(allbits):",len(allbits)
        #print "numints*128:",numints*128
        #assert len(allbits) == numints * 128
        #allbits = [int(allbits[i:i+64],2) for i in xrange(len(allbits) - 64, -1, -64)]
        #print "allbits:",allbits
        #self.source[:len(allbits)] = allbits
        #self.count.value = numbits
	chunksize = self.chunksize
	chunks = (numbytes + chunksize - 1)/chunksize
        out_data = StringIO.StringIO() 
	for chunk in range(chunks):
            data = StringIO.StringIO() 
            #data = BytesIO() 
            data.write(b"shift:")

            # comment next line
            #numbits = 16

            if chunk == chunks-1:
                mynumbits = numbits - (chunk*chunksize*8)
                mynumbytes = numbytes - (chunk*chunksize)
	    else:
		mynumbits = chunksize*8
		mynumbytes = chunksize

            value0 = mynumbits & 0xFF
            value1 = (mynumbits >> 8) & 0xFF
            value2 = (mynumbits >> 16) & 0xFF
            value3 = (mynumbits >> 24) & 0xFF
            #print "%i%i%i%i"%(value0, value1, value2, value3)
            data.write("%c%c%c%c"%(value0, value1, value2, value3))

            for i in range(chunk*chunksize, mynumbytes+chunk*chunksize):
                byte=tms[i*8:(i+1)*8]
                value = int(byte[::-1],2) & 0xFF
                data.write("%c"%value)

            for i in range(chunk*chunksize, mynumbytes+chunk*chunksize):
                byte=tdi[i*8:(i+1)*8]
                value = int(byte[::-1],2) & 0xFF
                data.write("%c"%value)

            #i think tms and tdi need to be formated similar to the block just above
            #data.write("%s%s"%(hex(int(tms))[2:10],hex(int(tdi))[2:10]))
            #data.write("%s%s"%(tms,tdi))
            # replace with data
            #data.write(b'\x40\x40\x41\x41') # to be replaced
            #data.write(b"%c%c"%(0x50,0x52))
            #print "String:",data.getvalue(),"--"
            self.s.send(data.getvalue())
            #print "S: "

            tdo_fromXVC = self.s.recv(mynumbytes)
            #print "got TDO "
            #print tdo_fromXVC
            for i in range(0, mynumbytes):
                ndigi=8
                if i == numbytes-1:
                    ndigi = 8-leftpad
                out_data.write("%s"%(('{0:0%ib}'%ndigi).format(ord(tdo_fromXVC[i]))[::-1]))

        #print out_data.getvalue()
        #print 'TDO',
        #pprint.pprint(out_data.getvalue())
        return out_data.getvalue()[::-1]
        #out_data = StringIO.StringIO() 
        #len_tdo=len(tdo_fromXVC)
        #print len_tdo
        #print ",",tdo_fromXVC[0],",",","
        #for i in range(0, len_tdo):
            #this_len = len(tdo_fromXVC[i])
            #print "this_len:",this_len
            
            #ele = bin(int(binascii.hexlify(tdo_fromXVC[i]), 16))[2:10]
            #print ele
            #ele = bin(int(binascii.hexlify(tdo_fromXVC[i]), 16))[2:this_len]
            #print len(ele)
            #print type(ele)
            #print "ele:",ele
            #out_data.write("%c"%ele)
            
        #tdo=bin(int(binascii.hexlify(tdo_fromXVC), 16))[2:len_tdo]
        #print out_data.getvalue()
        #print len(out_data.getvalue())
        #return out_data.getvalue()#_fromXVC
        #if usetdo:
        #    return allbits
        #else:



        #if not profile or numbits < 1000:
        #    check(DjtgPutTmsTdiBits, self, *self.wparams)

