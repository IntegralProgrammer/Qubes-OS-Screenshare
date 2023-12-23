#!/usr/bin/python3

import argparse
from subprocess import Popen, DEVNULL, PIPE

argparser = argparse.ArgumentParser()
argparser.add_argument('--from_qube', help="Qube to get the application screencast from", required=True)
argparser.add_argument('--to_qube', help="Qube to send the application screencast to", required=True)
argparser.add_argument('--window_id', help="Window ID in --from_qube of the application screen to share", required=True)
args = argparser.parse_args()

# Setup the inbound and outbound pipes
pipe_inbound = Popen(['cat'], stderr=DEVNULL, stdout=PIPE, stdin=PIPE)
pipe_outbound = Popen(['cat'], stderr=DEVNULL, stdout=PIPE, stdin=PIPE)

# Launch the "server" part of the screenshare application
proc_server = Popen(['qvm-run', '--pass-io', args.from_qube, '--', 'python3', '/usr/local/bin/qvm-screenshare-server.py', args.window_id], stderr=DEVNULL, stdout=pipe_outbound.stdin, stdin=pipe_inbound.stdout)
proc_client = Popen(['qvm-run', '--pass-io', args.to_qube, '--', 'python3', '/usr/local/bin/qvm-screenshare-client.py'], stderr=DEVNULL, stdout=pipe_inbound.stdin, stdin=pipe_outbound.stdout)

input("Sharing window: {} in Qube: {} with Qube: {}. Press Enter to exit.".format(args.window_id, args.from_qube, args.to_qube))

proc_client.terminate()
proc_server.terminate()
pipe_inbound.terminate()
pipe_outbound.terminate()

proc_client.wait()
proc_server.wait()
pipe_inbound.wait()
pipe_outbound.wait()

print("Finished")
