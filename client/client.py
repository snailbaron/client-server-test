import argparse, re, httplib
import xml.etree.ElementTree as ET
import json

class XmlDataBuilder:
    def __init__(self):
        self.root = ET.Element('root')

    def add(self, md5, name):
        data_el = ET.SubElement(self.root, 'data')
        md5_el = ET.SubElement(data_el, 'md5')
        md5_el.text = md5
        name_el = ET.SubElement(data_el, 'name')
        name_el.text = name

    def __str__(self):
        return ET.tostring(self.root)

class JsonDataBuilder:
    def __init__(self):
        self.root = []

    def add(self, md5, name):
        self.root.append({'md5': md5, 'name': name})

    def __str__(self):
        return json.dumps(self.root)

# Argument check: IP address
def arg_check_ip(ip_string):
    match = re.match(r'^(\d{1,3}).(\d{1,3}).(\d{1,3}).(\d{1,3})$', ip_string)
    if (match and all(int(s) <= 255 for s in match.groups())):
        return ip_string

    msg = 'Not a valid IP address: ' + ip_string
    raise argparse.ArgumentTypeError(msg)
    
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

if (args.format == 'xml'):
    builder = XmlDataBuilder()
elif (args.format == 'json'):
    builder = JsonDataBuilder()

# Read data file
with open(args.data) as f:
    for line in f:
        m = re.match(r'^(.*)&&&(.*)$', line)
        if m:
            builder.add(m.group(1), m.group(2))

con = httplib.HTTPConnection(args.ip)
con.request('POST', '/')
r = con.getresponse()
print r.status, r.reason