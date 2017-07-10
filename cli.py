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


def init_boost(args, feedback_queue):
    if isinstance(boost, ImportError):
        # Oops, Boost is needed but it couldn't be imported.
        raise boost

    boost.BoostCommunication(feedback_queue)

def init_local(args, feedback_queue):
    local.LocalCommunication(feedback_queue, args.filepath)

def init_rpc(args, feedback_queue):
    rpc.RPCCommunication(feedback_queue, args.ip_address, args.port, args.name)

def parse_and_initialize(feedback_queue):
    parser = argparse.ArgumentParser(description = 'User Simulator which can generate various types of traffic.')

    subparsers = parser.add_subparsers()
    boost_parser = subparsers.add_parser('boost')
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

    args = parser.parse_args()
    args.function(args, feedback_queue)
