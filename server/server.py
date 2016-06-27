import sys, os, logging, re, time, httplib, socket, ConfigParser, CGIHTTPServer, SocketServer
import errno

# Import module with data builders (common for client and server)
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.join('..', 'common')))
import builders

# Verbosity level for server logger. 
logging.basicConfig(level=logging.WARNING)

# Implementation of POST request handler on server
class Handler(CGIHTTPServer.CGIHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        CGIHTTPServer.CGIHTTPRequestHandler.__init__(self, request, client_address, server)
        
    # Process incoming POST request
    def do_POST(self):
        logging.info('POST request incoming')

        # Read info from request headers
        content_type = self.headers['Content-Type']
        content_length = int(self.headers['Content-Length'])
        logging.debug('Content type: {}'.format(content_type))
        logging.debug('Len: {}'.format(content_length))

        # Read request data        
        data = self.rfile.read(content_length)
        logging.debug('Data: {}'.format(data))
        
        # Create data builder of appropriate type
        # (depends on Content-Type in request header)
        if content_type == 'application/xml':
            builder = builders.XmlDataBuilder(data)
        elif content_type == 'application/json':
            builder = builders.JsonDataBuilder(data)
        else:
            self.send_response(415, 'Unsupported content type: {}'.format(content_type))
            return
        
        # Process each pair of keys
        response = []
        for d in builder.data:
            # Response values for current pair of keys are initially set to
            # 'None'. If requested key is found in a file, 'None' is replaced
            # with corresponding value.
            r = {'md5': 'None', 'name': 'None'}

            # Search values for current key pair in requested files            
            try:
                # Search file for MD5 keys
                with open(md5_file, 'r') as f_md5:
                    for md5_line in f_md5:
                        m = re.match(r'^(.*):(.*)$', md5_line)
                        if m:
                            if m.group(1) == d['md5']:
                                r['md5'] = m.group(2)
                        
                # Search file for string keys
                with open(string_file, 'r') as f_str:
                    for str_line in f_str:
                        m = re.match(r'^(.*):(.*)$', str_line)
                        if m:
                            if m.group(1) == d['name']:
                                r['name'] = m.group(2)
            except IOError, e:
                logging.error('Cannot read values file ({}): {}'.format(e.errno, e.strerror))
                self.send_response(500, 'Internal server error')
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                return

            # Add values for current pair of keys to response
            response.append(r)
                        
        # The same data builder is used to construct HTTP response, in the same
        # format
        builder.clear()
        builder.fill(response)
        
        # Set response code and headers. Use 200 (OK) code, and the same
        # Content-Type.
        self.send_response(200, 'OK')
        self.send_header('Content-Type', content_type)
        self.end_headers()

        # Fill response body with data, in the same format as incoming request.
        logging.debug('Response: {}'.format(builder.to_string()))
        self.wfile.write(builder.to_string())

# ThreadedServer is used instead of standard SocketServer.TCPServer to
# process incoming requests asynchronously.
class ThreadedServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


# Read server configuration file
config = ConfigParser.RawConfigParser({
    'port': 2222,
    'md5_file': 'md5_values.txt',
    'string_file': 'string_values.txt'
})
config.read('server.cfg')

port = config.getint('core', 'port')
md5_file = config.get('core', 'md5_file')
string_file = config.get('core', 'string_file')

try:
    # Create server, and listen to assigned port forever
    server = ThreadedServer(('', port), Handler)
    print "Serving at port:", port
    server.serve_forever()
except socket.error, e:
    logging.error('Cannot create server ({}): {}'.format(errno.errorcode[e.errno], e.strerror))