import re
import json
import time
import logging

try:
    from urllib.request import Request, urlopen
except ImportError:
    from urllib2 import Request, urlopen

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

try:
    from urllib.error import HTTPError, URLError
except ImportError:
    from urllib2 import HTTPError, URLError


__version__ = '0.1.0'


# ----------------------------------
# VERY DUMB AND BASIC HTTP METHODS
# ----------------------------------
# [*] Don't do this in a serious project !!! (use `requests`)

def get(url, with_content=True):
    """ Very basic HTTP GET """

    req, res = Request(url), None
    status, content = None, None

    try:
        res = urlopen(req, timeout=20)
    except HTTPError as e:
        status = int(re.search('[0-9]{3}', str(e)).group())
    except URLError as e:
        status = 0
    else:
        try:
            status = res.getcode() # Python 2
        except AttributeError:
            status = res.status # Python 3
        content = res.read() if with_content else None

    return status, content


def post(url, data):
    """ Basic HTTP POST. Expects the response as JSON. """

    data = bytes(urlencode(data).encode('utf-8'))
    req = Request(url, data)
    res = None
    status, content = None, None
    try:
        res = urlopen(req)
    except HTTPError as e:
        status = int(re.search('[0-9]{3}', str(e)).group())
    else:
        try:
            status = res.getcode() # Python 2
        except AttributeError:
            status = res.status # Python 3
        content = json.loads(res.read().decode('utf-8'))
    return status, content


# ----------------------
# PUSHOVER CLIENT
# ----------------------

class Pushover(object):
    """ Class for sending notifications via Pushover """

    URL =  'https://api.pushover.net/1/messages.json'

    def __init__(self, app_token, user_key):
        self.app_token = app_token
        self.user_key = user_key

    def send(self, msg, **kwargs):
        """ Send a notification to the user's device.
        Return `True` if successful, else `False` """

        payload = {'token': self.app_token, 'user': self.user_key}
        payload.update({'message': msg})
        payload.update(kwargs)
        status, content = post(self.URL, payload)
        return status == 200


# ----------------------
# MONITOR
# ----------------------

class Monitor(object):
    def __init__(self, sites, notifier, interval=60):
        self.urls = self.build_urls(sites)
        self.notifier = notifier
        self.interval = interval

    def build_urls(self, sites):
        """ Build the end urls """
        urls = []
        for site in sites:
            if not site.startswith('http'):
                url = 'http://{}/'.format(site)
            else:
                url = site
            urls.append(url)
        return urls

    def is_up(self, url):
        """ Check the url endpoint is healhty """
        status, _ = get(url)
        logging.debug('* Checking if {} is up [{}]'.format(url, status))
        return status == 200

    def check(self, url):
        """ Check if endpoint is healthy. Send a notification otherwise """
        ok = False
        try:
            ok = self.is_up(url)
        except Exception as e:
            logging.error(
                '* Error checking endpoint {}, '
                'error: {}'.format(url, str(e)))
        else:
            if not ok:
                self.notifier.send('Your site is down', url=url)

    def start(self):
        while True:
            for url in self.urls:
                self.check(url)
            logging.debug('* Sleeping for {} sec ...'.format(self.interval))
            time.sleep(self.interval)


# ----------------------
# CONFIG
# ------------------------------------

config = {
    'interval': 60,  # How often to perform checks (in seconds)
    'pushover': {
        'app_token': None,
        'user_key': None,
    },
    'sites': {
        'example.com', # Just the domain
        'http://example.com/hello',  # Or a full url
    }
}


# ----------------------
# MAIN
# ------------------------------------
def main():
    notifier = Pushover(**config['pushover'])
    monitor = Monitor(config['sites'], notifier, interval=config['interval'])
    notifier.send('critikl monitor started on {}'.format(time.ctime()))
    monitor.start()

if __name__ == '__main__':
    debug = False
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    main()
