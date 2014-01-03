#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import argparse
import logging
from ip_detector import IPDetector


def main():
    parser = argparse.ArgumentParser(description='Check the current external IP address.')
    parser.add_argument('-f', '--file',
                        nargs='?',
                        help='File to store the last IP address',
                        default='ip.txt')
    parser.add_argument('-l', '--log-level',
                        type=int,
                        choices=(1, 2, 3),
                        nargs='?',
                        help='Log level (error=1, normal=2, debug=3)',
                        default=2)
    parser.add_argument('-c', '--config',
                        nargs='?',
                        help='Config file',
                        default='IpUpdater.cfg')
    
    args = parser.parse_args()
    
    detector = IPDetector(args.config)
    
    if len(args.file) > 0:
        detector.setDataFile(args.file)

    if args.log_level != 2:
        detector.setLogLevel(args.log_level)

    (changed, ip) = detector.IpHasChanged()
    print 'IP address: %s (changed: %s)' % (ip, changed)
    

if __name__ == "__main__":
    main()
