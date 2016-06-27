import sys, os, argparse, re, httplib, logging
import xml.etree.ElementTree as ET
import json

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.join('..', 'common')))
import builders

# Verbosity level for client application logger
logging.basicConfig(level=logging.WARNING)

# Argument check: IP address
def arg_check_ip(ip_string):
    match = re.match(r'^(\d{1,3}).(\d{1,3}).(\d{1,3}).(\d{1,3})$', ip_string)
    if (match and all(int(s) <= 255 for s in match.groups())):
        return ip_string
    raise argparse.ArgumentTypeError('Not a valid IP address: {}'.format(ip_string))
    
# Define command line arguments
parser = argparse.ArgumentParser(description='Client app')
parser.add_argument('--ip', metavar='SERVER_IP', type=arg_check_ip, default='127.0.0.1',
    help='Server IP address')
parser.add_argument('--port', metavar='PORT', type=int, default=2222,
    help='Server port')
parser.add_argument('--format', metavar='FORMAT', choices=['xml', 'json'], default='xml',
    help='Format for request')
parser.add_argument('--data', metavar='FILE', default='default.txt',
    help='File with data')

# Parse command line
args = parser.parse_args()

print ''
print '--------------------------------------------------------------------------------'
print '  Server         : {0}:{1}'.format(args.ip, args.port)
print '  Request format : {0}'.format(args.format)
print '  Data file      : {0}'.format(args.data)
print '--------------------------------------------------------------------------------'
print ''

# Create a data builder for required data format (XML or JSON)
if (args.format == 'xml'):
    builder = builders.XmlDataBuilder()
elif (args.format == 'json'):
    builder = builders.JsonDataBuilder()

# Read data file
with open(args.data) as f:
    for line in f:
        m = re.match(r'^([0-9a-f]{32})&&&(.*)$', line)
        if m:
            logging.info("Adding to request: MD5={} : name={}".format(m.group(1), m.group(2)))
            builder.add(m.group(1), m.group(2))

# Set request headers (Content-Type) depending on data format
headers = {
    'Content-Type': builder.get_content_type()
}

# Send request to server
logging.info("sending request:\n{0}".format(builder.to_string()))
con = httplib.HTTPConnection(args.ip, args.port)
con.request('POST', '', builder.to_string(), headers)

# Get response from server
r = con.getresponse()
logging.info('response: {0} ({1})'.format(r.status, r.reason))
logging.info('Response headers: {}'.format(r.getheaders()))
resp_data = r.read()

# Read server response using the same data builder
builder.clear()
builder.read(resp_data)

print 'Server response:'
for d in builder.data:
    print "  MD5: {} String: {}".format(d['md5'], d['name'])
