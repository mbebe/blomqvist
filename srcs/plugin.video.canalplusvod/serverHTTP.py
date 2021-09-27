try:  # Python 3
    from http.server import BaseHTTPRequestHandler
except ImportError:  # Python 2
    from BaseHTTPServer import BaseHTTPRequestHandler

try:  # Python 3
    from socketserver import TCPServer
except ImportError:  # Python 2
    from SocketServer import TCPServer

try:  # Python 3
    from urllib.parse import parse_qs, urlparse, urlencode,quote,unquote
except ImportError:  # Python 2
    from urlparse import urlparse, parse_qs
    from urllib import urlencode,quote,unquote

import re

import xbmcaddon
import socket
from contextlib import closing

addon = xbmcaddon.Addon(id='plugin.video.canalplusvod')
import requests
import urllib3

requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

import sys
PY3 = sys.version_info >= (3,0,0)
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        """Handle http get requests, used for manifest"""
        path = self.path  # Path with parameters received from request e.g. "/manifest?id=234324"
        print('HTTP GET Request received to {}'.format(path))
        if '/manifest' not in path:
            self.send_response(404)
            self.end_headers()
            return
        try:
            # Call your method to do the magic to generate DASH manifest data
            manifest_data = b'my manifest data'
            self.send_response(200)
            self.send_header('Content-type', 'application/xml')
            self.end_headers()
            self.wfile.write(manifest_data)
        except Exception:
            self.send_response(500)
            self.end_headers()
            

    def do_POST(self):
        """Handle http post requests, used for license"""
        path = self.path  # Path with parameters received from request e.g. "/license?id=234324"
        print('HTTP POST Request received to {}'.format(path))
        if '/license' not in path:
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get('content-length', 0))
        isa_data = self.rfile.read(length).decode('utf-8').split('!')
        challenge = isa_data[0]
        if 'cense=' in path:
            path2 = path.split('cense=')[-1]
        
            licurl=(addon.getSetting('licurl'))
        
            ab=eval(addon.getSetting('hea'))
            result = requests.post(url=licurl, headers=ab, data=challenge,verify=False).content
            if PY3:
                result = result.decode(encoding='utf-8', errors='strict')
            licens=re.findall('ontentid=".+?">(.+?)<',result)[0]
            if PY3:
                licens= licens.encode(encoding='utf-8', errors='strict')
        elif 'censetv=' in path:
            path2 = path.split('censetv=')[-1]
        
            licurl=(addon.getSetting('lictvurl'))
        
            ab=eval(addon.getSetting('heatv'))
            result = requests.post(url=licurl, headers=ab, data=challenge,verify=False).json()
            licens=result['ServiceResponse']['OutData']['LicenseInfo']
            if PY3:

                licens= licens.encode(encoding='utf-8', errors='strict')

        self.send_response(200)
        self.end_headers()
        
        self.wfile.write(licens)

            
def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        addon.setSetting('proxyport',str(s.getsockname()[1]))
        return s.getsockname()[1]	       


address = '127.0.0.1'  # Localhost

port = find_free_port()

server_inst = TCPServer((address, port), SimpleHTTPRequestHandler)
# The follow line is only for test purpose, you have to implement a way to stop the http service!
server_inst.serve_forever()