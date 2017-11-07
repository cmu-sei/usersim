# Copyright 2017 Carnegie Mellon University. See LICENSE.md file for terms.

import sys
if sys.version_info.minor == 5:
    import py35.boostmq as boostmq


if __name__ == '__main__':
    with open('example.yaml') as f:
        config = f.read()

    config_mq = boostmq.MQ('config', 10, 50000)

    config_mq.sendqueue(config, 1)
