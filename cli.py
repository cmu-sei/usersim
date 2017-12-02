# Copyright 2017 Carnegie Mellon University. See LICENSE.md file for terms.

""" Gather and parse command line arguments.
"""
import argparse

try:
    from communication import boost
except ImportError as e:
    # This is fine if the Boost package was not bundled and Boost communication is not needed.
    boost = e
from communication import local
from communication import rpc
from communication import httpcomm


def parse_server_file(path):
    addresses = []
    with open(path) as f:
        try:
            with open(path) as f:
                lines = f.readlines()
        except OSError as e:
            print('Could not open the server file.')
            raise

        try:
            for i, line in enumerate(lines):
                addr, port = line.split(':')
                addresses.append((addr, int(port)))
        except ValueError as e:
            print('Could not parse the server file. Check line number %d.' % (i+1,))
            raise

    return addresses

def init_boost(args, feedback_queue):
    if isinstance(boost, ImportError):
        # Oops, Boost is needed but it couldn't be imported.
        raise boost

    boost.BoostCommunication(feedback_queue)

def init_local(args, feedback_queue):
    local.LocalCommunication(feedback_queue, args.filepath)

def init_rpc(args, feedback_queue):
    rpc.RPCCommunication(feedback_queue, args.ip_address, args.port, args.name)

def init_http(args, feedback_queue):
    if not args.file:
        args.file.append((args.ip_address, args.port))

    httpcomm.HTTPCommunication(feedback_queue, args.file, args.name, args.groups)

def test_mode(*args):
    return True

def parse_and_initialize(feedback_queue):
    parser = argparse.ArgumentParser(description = 'User Simulator which can generate various types of traffic.')

    subparsers = parser.add_subparsers()
    boost_parser = subparsers.add_parser('xga')
    boost_parser.set_defaults(function=init_boost)

    local_parser = subparsers.add_parser('local')
    local_parser.set_defaults(function=init_local)
    local_parser.add_argument('filepath',
            nargs='?',
            action='store',
            default='example.yaml',
            help='A YAML file with the tasks for the User Simulator.')

    rpc_parser = subparsers.add_parser('rpc')
    rpc_parser.set_defaults(function=init_rpc)
    rpc_parser.add_argument('ip_address',
            nargs='?',
            action='store',
            default='127.0.0.1',
            help='The server IP address.')
    rpc_parser.add_argument('port',
            nargs='?',
            action='store',
            default=18812,
            help='Server port to use.',
            type=int)
    rpc_parser.add_argument('name',
            nargs='?',
            action='store',
            default=None,
            help='An arbitrary identifier string for the RPC server to use.')

    http_parser = subparsers.add_parser('http')
    http_parser.set_defaults(function=init_http)
    http_parser.add_argument('name',
            action='store',
            help='An arbitrary identifier string for the http server to use.')
    http_parser.add_argument('-a', '--ip_address',
            nargs='?',
            action='store',
            default='127.0.0.1',
            help='The server IP address.')
    http_parser.add_argument('-p', '--port',
            nargs='?',
            action='store',
            default=5000,
            help='Server port to use.',
            type=int)
    http_parser.add_argument('-f', '--file',
            nargs='?',
            action='store',
            default=[],
            help='A path to a file containing multiple server address:port lines, in the case where the server is '
                 'sharded. The agent will pick from this list at random on startup and continue using that server '
                 'instance for its lifetime.',
            type=parse_server_file)
    http_parser.add_argument('-g', '--groups',
            nargs='+',
            action='store',
            default=[],
            help='A list of groups this agent belongs to.')

    test_parser = subparsers.add_parser('test')
    test_parser.set_defaults(function=test_mode)

    args = parser.parse_args()
    return args.function(args, feedback_queue)
