import requests
import time
import threading
from datetime import datetime
from datetime import timedelta

class Py3status:
    def post_config_hook(self):        
        """
        Runs the first time py3statusbar is initialized
        """
        self.thread_started = False
        self.time = None
        self.status = None
        self._time_format = '%d %b %H:%M' #Example: 26 Aug 19:02
        self._update_interval = 20 #Update status every 20 seconds
        self._api_url = 'https://omegav.no/api/dooropen.php'

    def _start_handler_thread(self):
        """Called once to start the event handler thread."""

        # Create handler thread
        t = threading.Thread(target=self._api_handler)
        t.daemon = True

        # Start handler thread
        t.start()
        self.thread_started = True

    def _api_handler(self):
        """
        Runs every n seconds, as defined in the post config hook method 
        """
        
        # Makes sure we update the status bar every n seconds
        threading.Timer(self._update_interval, self._api_handler).start()

        try:
            resp = requests.get(self._api_url)
            data = resp.json()
            
            self.status = data['open']
            self.time = data['time']  
        except:
            self.status = None
            self.time = None

        # Update py3statusbar
        self.py3.update()

    def _build_response(self):
        """
        Prepares the response to be sent back to py3status
        If the door is open: Display green text and date when opened
        If the door is closed: Display red text and date when closed
        If we somehow no longer cannot obtain door status, display blue text with error message
        """

        resp = {'color': '#000000', 
                'cached_until': self.py3.CACHE_FOREVER}
        today = datetime.now()

        if self.status == '1':
            time_opened = today - timedelta(seconds=int(self.time))
            resp['color'] = '#00FF00'
            resp['full_text'] = 'OV opened {0}'.format(time_opened.strftime(self._time_format))
        elif self.status == '0':
            time_closed = today - timedelta(seconds=int(self.time))
            resp['color'] = '#FF0000'
            resp['full_text'] = 'OV closed {0}'.format(time_closed.strftime(self._time_format)) 
        else:
            resp['color'] = '#0000FF' 
            resp['full_text'] = 'No connection to OV'
        
        return resp

    def omegav(self):
        if not self.thread_started:
            self._start_handler_thread()
        
        return self._build_response()
