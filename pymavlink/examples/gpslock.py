#!/usr/bin/env python

'''
show GPS lock events in a MAVLink log
'''

import sys, time, os

from optparse import OptionParser
parser = OptionParser("gpslock.py [options]")
parser.add_option("--condition", default=None, help="condition for packets")

(opts, args) = parser.parse_args()

import pymavlink.mavutil

if len(args) < 1:
    print("Usage: gpslock.py [options] <LOGFILE...>")
    sys.exit(1)

def lock_time(logfile):
    '''work out gps lock times for a log file'''
    print("Processing log %s" % filename)
    mlog = mavutil.mavlink_connection(filename)

    locked = False
    start_time = 0.0
    total_time = 0.0
    t = None
    m = mlog.recv_match(type=['GPS_RAW_INT','GPS_RAW'], condition=opts.condition)
    if m is None:
        return 0

    unlock_time = time.mktime(time.localtime(m._timestamp))

    while True:
        m = mlog.recv_match(type=['GPS_RAW_INT','GPS_RAW'], condition=opts.condition)
        if m is None:
            if locked:
                total_time += time.mktime(t) - start_time
            if total_time > 0:
                print("Lock time : %u:%02u" % (int(total_time)/60, int(total_time)%60))
            return total_time
        t = time.localtime(m._timestamp)
        if m.fix_type >= 2 and not locked:
            print("Locked at %s after %u seconds" % (time.asctime(t),
                                                     time.mktime(t) - unlock_time))
            locked = True
            start_time = time.mktime(t)
        elif m.fix_type == 1 and locked:
            print("Lost GPS lock at %s" % time.asctime(t))
            locked = False
            total_time += time.mktime(t) - start_time
            unlock_time = time.mktime(t)
        elif m.fix_type == 0 and locked:
            print("Lost protocol lock at %s" % time.asctime(t))
            locked = False
            total_time += time.mktime(t) - start_time
            unlock_time = time.mktime(t)
    return total_time

total = 0.0
for filename in args:
    total += lock_time(filename)

print("Total time locked: %u:%02u" % (int(total)/60, int(total)%60))
