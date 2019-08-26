#!/usr/bin/python3

# server for js impress remote

import json
from collections import OrderedDict
from geventwebsocket import WebSocketServer, WebSocketApplication, Resource

# TODO create some interface(?) in unoremote.py to inherit from
class Libo ():
    def on_slideshow_started (self, num_slides, current_slide):
        data = json.dumps(
            {
                "action"        : "slideshow_started",
                "slide_count"   : num_slides,
                "current_slide" : current_slide
            })
        send_all(data)

    def on_slideshow_ended (self):
        send_all('{"action" : "slideshow_finished"}')

    def on_slide_notes (self, slide_index, html):
        data = json.dumps(
            {
                "action"        : "slide_notes",
                "slide_index"   : slide_index,
                "html"          : html 
            })
        send_all(data)

    def on_slide_updated (self, slide_index):
        data = json.dumps(
            {
                "action"        : "slide_updated",
                "slide_index"   : slide_index,
            })
        send_all(data)

    def on_slide_preview (self, slide_index, image):
        data = json.dumps(
            {
                "action"        : "slide_preview",
                "slide_index"   : slide_index,
                "image"         : image
            })
        send_all(data)

    def focus_info_screen (self):
        pass

    def error_no_document (self):
        print('error: no document')

def send_all (msg):
    for ws in clients:
        ws.send(msg)

clients = []

class IRPApp (WebSocketApplication):
    def on_open (self):
        global clients
        clients.append(self.ws)
        self.connected = False

        print("new conn")

    def on_message (self, message):

        # handshake
        if '\"hello\"' == message:
            self.ws.send('hello')
            self.connected = True
            uno.send_slide_info()
            print('recv handshake')

        # disconnected
        elif None == message:
            # TODO do something?
            pass

        else:
            data = json.loads(message)
            self.irp_msg(data)

    def irp_msg (self, msg):
        action = msg["action"]

        # TODO add exceptions for msg["xxxx"] in case there's no such key

        # NOTE it could be imagined that we'd want to process/ make checks
        #      before calling the UNOClient methods
        if 'transition_next' == action:
            uno.transition_next()

        elif 'transition_previous' == action:
            uno.transition_previous()

        elif 'goto_slide' == action:
            number = msg["number"]
            uno.goto_slide(number)

        elif 'presentation_start' == action:
            uno.presentation_start()

        elif 'presentation_stop' == action:
            uno.presentation_stop()

        elif 'presentation_blank_screen' == action:
            uno.blank_screen()

        elif 'presentation_resume' == action:
            uno.resume()

    def on_close (self, reason):
        global clients
        clients.remove(self.ws)

        print("close", reason)

def run_irp_server(address = '0.0.0.0', port = 5100):
    addr = (address, port)
    WebSocketServer(addr, Resource(OrderedDict([('/', IRPApp)]))).serve_forever()

if __name__ == '__main__':
    import sys
    # TODO get cmd line arg for path
    import libresign.unoremote as unoremote
    
    control = Libo()
    uno = unoremote.UNOClient(control)
    uno.start(True)

    run_irp_server()

