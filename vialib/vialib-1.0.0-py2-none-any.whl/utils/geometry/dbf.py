#######################################################################
#
#       COPYRIGHT 2006 MAYA DESIGN, INC., ALL RIGHTS RESERVED.
#
# ALL INTELLECTUAL PROPERTY RIGHTS IN THIS PROGRAM ARE OWNED BY MAYA DESIGN.
# THIS PROGRAM CONTAINS CONFIDENTIAL AND PROPRIETARY INFORMATION OWNED BY MAYA
# DESIGN AND MAY NOT BE DISCLOSED TO ANY THIRD PARTY WITHOUT THE PRIOR CONSENT
# OF MAYA DESIGN.  THIS PROGRAM MAY ONLY BE USED IN ACCORDANCE WITH THE TERMS
# OF THE APPLICABLE LICENSE AGREEMENT FROM MAYA DESIGN. THIS LEGEND MAY NOT BE
# REMOVED FROM THIS PROGRAM BY ANY PARTY.
#
# THIS LEGEND AND ANY MAYA DESIGN LICENSE DOES NOT APPLY TO ANY OPEN SOURCE
# SOFTWARE THAT MAY BE PROVIDED HEREIN.  THE LICENSE AGREEMENT FOR ANY OPEN
# SOURCE SOFTWARE, INCLUDING WHERE APPLICABLE, THE GNU GENERAL PUBLIC LICENSE
# ("GPL") AND OTHER OPEN SOURCE LICENSE AGREEMENTS, IS LOCATED IN THE SOURCE
# CODE FOR SUCH SOFTWARE.  NOTHING HEREIN SHALL LIMIT YOUR RIGHTS UNDER THE
# TERMS OF ANY APPLICABLE LICENSE FOR OPEN SOURCE SOFTWARE.
#######################################################################

import struct
import time
import string

from MAYA.VIA import vsmf
from MAYA.utils import date
import MAYA.datatypes

# remove null characters from a string and whitespace from ends
def clean(s):
    try:
        s = s.decode('utf8')
    except UnicodeDecodeError:
        s = s.decode('latin-1')
    s = filter(lambda x: x != '\0', s)
    return s.strip()

def make_num(n):
    t = type(n)
    if t in (int, long):
        return n
    elif t is float:
        if n % 1.0 == 0.0:
            return int(n)
        else:
            return n
    elif t in (str, unicode):
        return make_num(eval(n))
    else:
        return n

def clean_numeric(s):
    def f(c):
	return c in ('-','+','.','0','1','2','3','4','5','6','7','8','9','0','e','E')
    s = filter(f, s)
# why did I do this?
#     if '.' not in s:
# 	s = s.strip('0')
# 	if not s:
# 	    return '0'
    return s

class DBFWriter:

    def __init__(self, efs):
        self.efs = efs

    def write_header(self, fdl):
        ef = self.efs[0]
        n_attrs = len(ef.keys())
        len_record = 127*n_attrs + 1
        
        buf = struct.pack('<b', 0x83)

        # my birthday
        buf = buf + struct.pack('<b', 75)
        buf = buf + struct.pack('<b', 10)
        buf = buf + struct.pack('<b', 11)    
        
        buf = buf + struct.pack('<l', len(self.efs))
        buf = buf + struct.pack('<h', 32 + fdl + 1)
        buf = buf + struct.pack('<h', len_record)
        buf = buf + struct.pack('<bbb', 0, 0, 0) # 3 bytes
        buf = buf + struct.pack('<lllb', 0, 0, 0, 0) # 13 bytes
        buf = buf + struct.pack('<l', 0) # 4 bytes

        return buf

    def write_field_descriptor(self):
        attrs = self.efs[0].keys()
        attrs.sort()

        fda = ''
        for attr in attrs:
            buf = struct.pack('<11s', attr)
            buf = buf + struct.pack('<c', 'C')
            buf = buf + struct.pack('<i', 0)
            buf = buf + struct.pack('<b', 127)
            buf = buf + struct.pack('<15s', '')
            fda = fda + buf

        return fda

    def write_records(self):
        buf = ''
        for ef in self.efs:
            record = struct.pack('<b', 0x20)
            attrs = ef.keys()
            attrs.sort()
            for attr in attrs:
                value = ef[attr]
                record = record + struct.pack('<127s', value)
            buf = buf + record
        return buf

    def end_of_header(self):
        return struct.pack('<b', 0x0d)
                
    def end_of_file(self):
        return struct.pack('<b', 0x1a)

    def write(self, name):
        fields = self.write_field_descriptor()
        records = self.write_records()
        eof = self.end_of_file()
        eoh = self.end_of_header()
        fdl = len(fields)
        header = self.write_header(fdl)

        buf = header + fields + eoh + records + eof
        fd = open(name, 'w')
        fd.write(buf)
        fd.close()

        return

class DBF:

    def __init__(self, fn, verbose=0):
        self.fn = fn
        self.verbose = verbose

    def read_header(self):
        self.version = struct.unpack("<b", self.fd.read(1))[0]
        self.year_update = struct.unpack("<b", self.fd.read(1))[0]
        self.month_update = struct.unpack("<b", self.fd.read(1))[0]
        self.day_update = struct.unpack("<b", self.fd.read(1))[0]
        self.n_records = struct.unpack("<l", self.fd.read(4))[0]
        self.header_length = struct.unpack("<h", self.fd.read(2))[0]
        self.record_length = struct.unpack("<h", self.fd.read(2))[0]
        self.fd.read(20) # reserved

        self.field_descriptors = []
        i = 32
        while i < (self.header_length - 1):
            field_name = self.fd.read(11)
            field_type = self.fd.read(1)
            self.fd.read(4) # reserved
            field_length = struct.unpack("<B", self.fd.read(1))[0]
            self.fd.read(15)
            i = i + 32

            field = { 'name':clean(field_name), 'type':field_type,
                      'length':field_length }

	    self.field_descriptors.append(field)

        terminator = struct.unpack("<b", self.fd.read(1))[0]
        if terminator != 13:
            print "ERROR terminating header", terminator

        if self.verbose:
            print self.field_descriptors

    def getFieldNames(self):
	return [ field['name'] for field in self.field_descriptors ]

    def handle_field(self, record, field, data):
        if field['type'] == 'C':
            record[field['name']] = clean(data)
        elif field['type'] == 'N':
	    x = clean_numeric(data)
	    if x:
		x = make_num(x)
	    else:
		x = None
	    record[field['name']] = x
        elif field['type'] == 'F': # hrm?
	    x = clean_numeric(data)
	    if x:
		x = make_num(x)
	    else:
		x = None
	    record[field['name']] = x
        elif field['type'] == 'L':
            v = data[0].lower()
            if v == '?':
                value = None
            elif v == 'y':
                value = MAYA.datatypes.True
            elif v == 't':
                value = MAYA.datatypes.True
            elif v == 'n':
                value = MAYA.datatypes.False
            elif v == 'f':
                value = MAYA.datatypes.False
            record[field['name']] = value
        elif field['type'] == 'D':
	    try:
		t = time.mktime(time.strptime(data, "%Y%m%d"))
		d = date.fromUnix(t)
		record[field['name']] = d
	    except:
		record[field['name']] = None
        else:
            print "ERROR Unknown type!", field['type']
            record[field['name']] = None
        return record

    def read_records(self):

        records = []

        while 1:
	    try:
		deleted = struct.unpack("<b", self.fd.read(1))[0]
	    except: # DBF files are supposed to end in EOF, but sometimes not
		break
            if deleted == 26: # EOF
                break
            record = {}
            for field in self.field_descriptors:
                data = self.fd.read(field['length'])
                if deleted == 32:
                    record = self.handle_field(record, field, data)
            if deleted == 32:
                records.append(record)
	    if self.verbose:
		print record

        self.records = records
        return self.records

    def open(self):
        self.fd = open(self.fn, 'r')
        self.read_header()

        if self.verbose:
            print "DBF Version", self.version
            print "Last updated", self.month_update, "/", self.day_update, "/", self.year_update
            print self.n_records, "records"
            print "Header length", self.header_length

        self.read_records()
        self.fd.close()

        return self.records

    def tsv(self, name):
        if self.verbose:
            print "Dumping tab-separated values to", name
        fd = open(name, 'w')
        record = self.records[0]
        keys = record.keys()
        keys.sort()
        header = string.join(keys, '\t')
        fd.write(header + '\n')

        for record in self.records:
            values = []
            for key in keys:
                values.append(str(record[key]))
            v = string.join(values, '\t')
            fd.write(v + '\n')
        fd.close()

    def dump(self):
        for record in self.records:
            keys = record.keys()
            keys.sort()
            for key in keys:
                print key, record[key]
            print

def test():
    db = DBF('/Users/sui66iy/Documents/Downloads/zip1999 Folder/zipnov99.DBF', 1)
    db.open()
    db.tsv('zipcodes.tsv')

def wr_test():
    efs  = [{'name': 'Michael Higgins', 'age': '29', 'job': 'Programmer'},
            {'name': 'Grandma Jean', 'age': '91', 'job': 'Grandmother'},
            {'name': 'George W. Bush', 'age': '55?', 'job': 'President'},
            {'name': 'John F. Kerry', 'age': '55?', 'job': 'Senator'}]
    dbw = DBFWriter(efs)
    dbw.write('jobs.dbf')
    db = DBF('jobs.dbf')
    db.open()
    db.tsv('jobs.tsv')
    return

if __name__ == '__main__':
    wr_test()
    
        
