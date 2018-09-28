import argparse

parser = argparse.ArgumentParser(description='Help to define mode of tool.', add_help=False)
parser.add_argument('-h', '--help', action='help', help='Help message about modes of tool.')
parser.add_argument('-d', '--default', dest='input', action='store_const', const='default', help='Default mode: in this mode, script will get data from 0:00 yesterday to 0:00 present day.')
parser.add_argument('-u', '--user', dest='input', action='store_const', const='user', help='User mode: user define time for script to get data. Format for time is: yyyy-mm-dd hh:mm:ss (support 24hours).')
args = parser.parse_args()
global action
action = args.input




