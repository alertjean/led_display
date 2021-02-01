#!/usr/bin/env python
# Note: run pigpiod as sudo in the background

import time
import pigpio
import feedparser
import random
from rss import links
import sys
import datetime as dt
import os
import urllib
import threading
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer # python2
import Queue as queue

lookup =  {
           ' ': 0x20 , ' ': 0x40 , ' ': 0x60 , 'mb1': 0x80,
           '!': 0x21 , 'A': 0x41 , 'a': 0x61 , 'mb2': 0x81,
           '"': 0x22 , 'B': 0x42 , 'b': 0x62 , 
           '#': 0x23 , 'C': 0x43 , 'c': 0x63 ,
           '$': 0x24 , 'D': 0x44 , 'd': 0x64 ,
           ' ': 0x25 , 'E': 0x45 , 'e': 0x65 ,
           ' ': 0x26 , 'F': 0x46 , 'f': 0x66 ,
          '\'': 0x27 , 'G': 0x47 , 'g': 0x67 ,
           '(': 0x28 , 'H': 0x48 , 'h': 0x68 ,
           ')': 0x29 , 'I': 0x49 , 'i': 0x69 ,
           '*': 0x2A , 'J': 0x4A , 'j': 0x6A ,
           ' ': 0x2B , 'K': 0x4B , 'k': 0x6B ,
           ',': 0x2C , 'L': 0x4C , 'l': 0x6C ,
           '-': 0x2D , 'M': 0x4D , 'm': 0x6D ,
           '.': 0x2E , 'N': 0x4E , 'n': 0x6E ,
           '/': 0x2F , 'O': 0x4F , 'o': 0x6F ,
           '0': 0x30 , 'P': 0x50 , 'p': 0x70 ,
           '1': 0x31 , 'Q': 0x51 , 'q': 0x71 ,
           '2': 0x32 , 'R': 0x52 , 'r': 0x72 ,
           '3': 0x33 , 'S': 0x53 , 's': 0x73 ,
           '4': 0x34 , 'T': 0x54 , 't': 0x74 ,
           '5': 0x35 , 'U': 0x55 , 'u': 0x75 ,
           '6': 0x36 , 'V': 0x56 , 'v': 0x76 ,
           '7': 0x37 , 'W': 0x57 , 'w': 0x77 ,
           '8': 0x38 , 'X': 0x58 , 'x': 0x78 ,
           '9': 0x39 , 'Y': 0x59 , 'y': 0x79 ,
           ':': 0x3A , 'Z': 0x5A , 'z': 0x7A ,
           ' ': 0x3B , ' ': 0x5B , ' ': 0x7B ,
           '<': 0x3C , ' ': 0x5C , ' ': 0x7C ,
           '=': 0x3D , ' ': 0x5D , ' ': 0x7D ,
           '>': 0x3E , ' ': 0x5E , ' ': 0x7E ,
           '?': 0x3F , ' ': 0x5F , ' ': 0x7F
        }
    

def get_wave(byte):
    byte_wave = [];
    #out = '';
    for i in (7,6,5,4,3,2,1,0):
        if(((byte>>i) & 1)==1):
            byte_wave.append(one)
    #        out+='1'
        else:
            byte_wave.append(zero)
    #        out+='0'
    #print out
    return byte_wave

# 38.5 pulses for 1ms
def get_zero_mod(gpio):
    one_mod = []
    for i in range (0,38):
        one_mod.append(pigpio.pulse(1<<gpio, 0      , 13   )) # 38.46kHz Square wave
        one_mod.append(pigpio.pulse(0      , 1<<gpio, 13   )) #
    one_mod.append(pigpio.pulse(0     , 1<<gpio, 13   ))
    return one_mod

def get_one_mod(gpio):
    zero_mod = []
    zero_mod.append(pigpio.pulse   (0      , 0      , ((38*26)+13)))
    return zero_mod


def fix_line(line):
    max_length = 36
    length = len(line)
    if(length < max_length):
        line+=' ' * (max_length-length)
    elif(length > max_length):
        line =line[:max_length]
    return line

def get_display_line(single_line):
    lines = []
    max_length = 36
    space_length = max_length - (len(single_line)% max_length)
    single_line+=' ' * space_length
    old_chunk = ' ' * max_length
    while single_line:
        chunk = single_line[:max_length]
        single_line = single_line[max_length:]
        lines.append(old_chunk[(max_length/2):max_length]+chunk[:(max_length/2)])
        lines.append(chunk)
        old_chunk = chunk
    return lines

def get_news_loop():
    while True:
        print 'Waiting to fill news queue'
        news=get_news(5000)
        print "Fresh news ready!"
        news_q.put(news)
        print 'Filled news queue'

def get_news(news_length):
    news = ""
    #for country in links.keys():
        #for category in random.sample(links[country].keys(),1):
            #for link in random.sample(links[country][category].keys(),1):
    country  = random.sample(('US','IN'),1)[0]
    #country  = random.sample(('IN'),1)[0]
    category = random.sample(('general','business','science','tech','entertainment','politics'),1)[0]
    #category = random.sample(('kerala'),1)[0]
    i=0
    print 'Getting news {} {} {}'.format(country,category,news_length)
    while True:
        link     = random.sample(links[country][category].keys(),1)[0]
        #print "Collecting news from [{0}][{1}][{2}]".format(country,category,link)
        feed = feedparser.parse(link)
        items = feed["items"]
        if(len(items)==0):
            i=i+1
            if(i==10):
                print 'Waiting for internet'
                time.sleep(10)
                i=0
        else:
            i=0
        try:
            for item in items:
                if item.has_key("title"):
                    title = item["title"]
                    if(title.count(' ')<3): # Remove short phrases 
                        continue
                    #print("[{0}]".format(title))
                    news+=title + ' '* 30 + title + ' '* 30 
                    print 'New length {}'.format(len(news))
                    if(len(news)>news_length):
                        return(news)

                else:
                    print "No title {}".format(link)
        except ValueError:
            pass 
            print "Failure {}".format(link)
def get_char_code(char):
    if(lookup.has_key(char)):
        return(lookup[char])
    else:
        return(lookup[' '])

def get_line_wave(line):
    final_wave =[]
    final_wave.extend(get_wave(0xff))
    final_wave.extend(get_wave(0xff))
    final_wave.extend(get_wave(0x04))
    for char in line:
         final_wave.extend(get_wave(get_char_code(char)))
    final_wave.extend(get_wave(0xff))
    final_wave.extend(get_wave(0xff))
    final_wave.extend(get_wave(0xff))
    final_wave.extend(get_wave(0xff))
    return final_wave

def check_hours(hours,wait=False):
    while True:
        now=dt.datetime.now()
        if(now.hour in hours):
            if wait is True:
                print 'Waiting hour {}'.format(now.hour)
                time.sleep(600)
            else:
                return True
        else:
            return False

class HandleRequests(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        with open('/home/pi/display/home.html','r') as f:
            html=f.read()
        self._set_headers()
        self.wfile.write(html)

    def do_POST(self):
        '''Reads post request body'''
        self._set_headers()
        content_len = int(self.headers.getheader('content-length', 0))
        post_body = self.rfile.read(content_len)
        message=str(urllib.unquote(post_body))
        if message.startswith('display_message='):
            message=message.replace('display_message=','')
            server_q.put(message)
        if message.startswith('reboot=1'):
            message = 'Rebooting now..'
            self.wfile.write(message)
            print message
            server_q.put(message)
            os.system('sudo reboot now')
        with open('/home/pi/display/home.html','r') as f:
            html=f.read()
        self.wfile.write(html)
        print 'Display [{}]'.format(message)
        
    def do_PUT(self):
        self.do_POST()
    
def run_server(): 
    host = ''
    port = 80
    print 'Starting web server'
    HTTPServer((host, port), HandleRequests).serve_forever()

def main_loop():
    #single_line = ""
    #for line in lyrics:
    #    single_line=single_line+line+(" " * 10)
    initial=1
    server=threading.Thread(target=run_server,      args=())
    news  =threading.Thread(target=get_news_loop  , args=())
    news.daemon=True
    news.start()
    server.daemon=True
    server.start()
    print 'Started web server'
    while True:
        if(initial == 1):
            single_line = "Welcome!"
            initial = 0
        elif not server_q.empty():
            print "Got server request"
            single_line=server_q.get()
            single_line+=' ' * 20
            single_line=single_line * 4
            server_q.task_done()
        else:
            single_line=news_q.get(block=True)
            print "Got news to display"
        lines = get_display_line(single_line)
        print "Display start"
        old_time=time.time();
        for line in lines:
            if not server_q.empty():
                break
            new_time=time.time();
            print '[{}][{:0.6f}]'.format(line.encode('utf-8'),new_time-old_time-3.30)
            final_wave = get_line_wave(line)
            pi.wave_chain(final_wave)
            old_time=new_time
            #time.sleep(3.230) # One rotation takes this much time
            #time.sleep(3.280) # One rotation takes this much time
            #time.sleep(3.300) # One rotation takes this much time
            time.sleep(3.290) # One rotation takes this much time # Clean time
            #time.sleep(3.380) # One rotation takes this much time
            #time.sleep(3.400) # One rotation takes this much time
            #time.sleep(3.420) # One rotation takes this much time


########### Main 
time.sleep(5)
pi=pigpio.pi()
print "Maximum waveform size is %dus\n" % pi.wave_get_max_micros()

if not pi.connected:
   exit()
pi.set_mode(4, pigpio.OUTPUT) # GPIO 4
one_mod  = get_one_mod(4); 
zero_mod = get_zero_mod(4); 
pi.wave_clear()
pi.wave_add_generic(one_mod)
one = pi.wave_create()
pi.wave_add_generic(zero_mod)
zero = pi.wave_create()

server_q = queue.Queue()
news_q   = queue.Queue(maxsize=1)
main_loop()


