import ConfigParser, CGIHTTPServer, SocketServer

config = ConfigParser.RawConfigParser()
config.read('server.cfg')

port = config.getint('core', 'port')
md5_file = config.get('core', 'md5_file')
string_file = config.get('core', 'string_file')

class Handler(CGIHTTPServer.CGIHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        CGIHTTPServer.CGIHTTPRequestHandler.__init__(request, client_address, server)

    def do_POST(self):
        print 'I got a POST'

server = SocketServer.TCPServer(('', port), Handler)

print "Serving at port:", port
server.serve_forever()