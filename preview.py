import SimpleHTTPServer
import SocketServer
import os
from sys import argv
import signal
from larklib import Site

# set PORT
PORT = 8000
if len(argv) > 1: PORT = int(argv[1])

# get site details
site = Site().config_vars

# get current directory
current_directory = os.getcwd()

# change to output directory
os.chdir( site.output_path )

# set up server
Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
httpd = SocketServer.TCPServer(("", PORT), Handler)

# print output
print "Serving on PORT %s \nView in browser at http://localhost:%s" % (PORT, PORT)

# initiate server
httpd.serve_forever()

# change back to original directory
os.chdir( current_directory )

# Free up the port when we kill the server
def signal_handler(signal, frame):
	httpd.shutdown()
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

