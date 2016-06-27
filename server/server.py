import sys, os, logging, re, time, httplib, ConfigParser, CGIHTTPServer, SocketServer

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.join('..', 'common')))
import builders

class Handler(CGIHTTPServer.CGIHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        CGIHTTPServer.CGIHTTPRequestHandler.__init__(self, request, client_address, server)
        
    def do_GET(self):
        logging.debug('I got a GET')

    def do_POST(self):
        logging.debug('I got a POST')

        time.sleep(1)
        
        content_type = self.headers['Content-Type']
        
        logging.info('Headers')
        logging.info('{}'.format(self.headers))
        
        logging.info('Content type: {}'.format(content_type))
        
        content_length = int(self.headers['Content-Length'])
        logging.debug('Len: {}'.format(content_length))
        
        data = self.rfile.read(content_length)
        logging.debug('Data: {}'.format(data))
        
        if content_type == 'application/xml':
            builder = builders.XmlDataBuilder(data)
        elif content_type == 'application/json':
            builder = builders.JsonDataBuilder(data)
        else:
            self.send_response(415, 'Unsupported content type: {0}'.format(content_type))
            return
            
        response = []
        for d in builder.data:
            r = {'md5': 'None', 'name': 'None'}
            
            with open(md5_file, 'r') as f_md5:
                for md5_line in f_md5:
                    logging.debug('MD5 line: {}'.format(md5_line))
                    m = re.match(r'^(.*):(.*)$', md5_line)
                    if m:
                        logging.debug('Match')
                        logging.debug('Key: {}'.format(m.group(1)))
                        logging.debug('What we have: {}'.format(d['md5']))
                        if m.group(1) == d['md5']:
                            logging.debug('Key matches')
                            r['md5'] = m.group(2)
                    
            with open(string_file, 'r') as f_str:
                for str_line in f_str:
                    m = re.match(r'^(.*):(.*)$', str_line)
                    if m:
                        if m.group(1) == d['name']:
                            r['name'] = m.group(2)
                            
            response.append(r)
                        
        builder.clear()
        builder.fill(response)
        
        self.send_response(200, 'OK')
        self.send_header('Content-Type', content_type)
        self.end_headers()
        
        logging.info('Writing: {}'.format(builder.to_string()))
        
        self.wfile.write(builder.to_string())

class ThreadedServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.WARNING)

config = ConfigParser.RawConfigParser()
config.read('server.cfg')

port = config.getint('core', 'port')
md5_file = config.get('core', 'md5_file')
string_file = config.get('core', 'string_file')

#server = SocketServer.TCPServer(('', port), Handler)
server = ThreadedServer(('', port), Handler)

print "Serving at port:", port
server.serve_forever()