#!/usr/bin/env python
import urllib
import threading
import time

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer # python2
#from http.server import BaseHTTPRequestHandler, HTTPServer # python3
class HandleRequests(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        with open('home.html','r') as f:
            html=f.read()
        self._set_headers()
        self.wfile.write(html)

    def do_POST(self):
        '''Reads post request body'''
        self._set_headers()
        content_len = int(self.headers.getheader('content-length', 0))
        post_body = self.rfile.read(content_len)
        with open('home.html','r') as f:
            html=f.read()
        self.wfile.write(html)
        #print 'Display [{}]'.format(urllib.unquote(post_body.replace('display_message=','')))
        print 'Display [{}]'.format(urllib.unquote(post_body))
        
    def do_PUT(self):
        self.do_POST()
    
    def handle_error(self, request, client_address):
        print 'Request error'
        print request
        pass

def run_server(): 
    host = ''
    port = 80
    print 'Starting web server'
    HTTPServer((host, port), HandleRequests).serve_forever()
 

server=threading.Thread(target=run_server, args=())
server.daemon=True
server.start()
print 'Started web server'
while True:
    time.sleep(10)

