# Copyright 2017 Carnegie Mellon University. See LICENSE.md file for terms.

class HTTPCommunication(object):
    def __init__(self, feedback_queue, ip_addr, port, name, groups):
        print('\nIP Address: {}\nPort: {}\nName: {}\nGroups: {}'.format(ip_addr, port, name, groups))
