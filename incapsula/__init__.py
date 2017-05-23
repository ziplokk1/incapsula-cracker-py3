from __future__ import unicode_literals

import datetime
import logging
import random

from six.moves.urllib.parse import quote, urlsplit

from bs4 import BeautifulSoup
from requests import Session

logger = logging.getLogger()

o = [
    ('navigator', 'true'),
    ('navigator.vendor', 'Google Inc.'),
    ('navigator.appName', 'Netscape'),
    ('navigator.plugins.length==0', 'false'),
    ('navigator.platform', 'Linux x86_64'),
    ('navigator.webdriver', 'undefined'),
    ('plugin_ext', 'no extention'),
    ('plugin_ext', 'so'),
    ('ActiveXObject', 'false'),
    ('webkitURL', 'true'),
    ('_phantom', 'false'),
    ('callPhantom', 'false'),
    ('chrome', 'true'),
    ('yandex', 'false'),
    ('opera', 'false'),
    ('opr', 'false'),
    ('safari', 'false'),
    ('awesomium', 'false'),
    ('puffinDevice', 'false'),
    ('__nightmare', 'false'),
    ('_Selenium_IDE_Recorder', 'false'),
    ('document.__webdriver_script_fn', 'false'),
    ('document.$cdc_asdjflasutopfhvcZLmcfl_', 'false'),
    ('process.version', 'false'),
    ('navigator.cpuClass', 'false'),
    ('navigator.oscpu', 'false'),
    ('navigator.connection', 'false'),
    ('window.outerWidth==0', 'false'),
    ('window.outerHeight==0', 'false'),
    ('window.WebGLRenderingContext', 'true'),
    ('document.documentMode', 'undefined'),
    ('eval.toString().length', '33')
]


def test():
    r = [quote('='.join(x), safe='()') for x in o]
    return ','.join(r)


def simple_digest(s):
    """

    Translated From:
    ```javascript
    function simpleDigest(mystr) {
        var res = 0;
        for (var i = 0; i < mystr.length; i++) {
            res += mystr.charCodeAt(i);
        }
        return res;
    }
    ```
    :param s: 
    :return: 
    """
    res = 0
    for ch in s:
        res += ord(ch)
    return str(res)


class IncapSession(Session):
    MAX_INCAP_RETRIES = 3

    def __init__(self, *args, **kwargs):
        super(IncapSession, self).__init__(*args, **kwargs)
        self.headers['User-Agent'] = 'IncapUnblockSession (sdscdeveloper@gmail.com | https://github.com/ziplokk1/incapsula-cracker-py3)'

    def get_session_cookies(self):
        """
        Get cookies from the session tu use with set_incap_cookie.

        Translated from:

        ```javascript
        function getSessionCookies() {
            var cookieArray = new Array();
            var cName = /^\s?incap_ses_/;
            var c = document.cookie.split(";");
            for (var i = 0; i < c.length; i++) {
                var key = c[i].substr(0, c[i].indexOf("="));
                var value = c[i].substr(c[i].indexOf("=") + 1, c[i].length);
                if (cName.test(key)) {
                    cookieArray[cookieArray.length] = value;
                }
            }
            return cookieArray;
        }
        ```
        :param self: 
        :return: 
        """
        a = []
        for cookie in self.cookies:
            if cookie.name.startswith('incap_ses_'):
                a.append(cookie.value)
        return a

    def create_cookie(self, name, value, seconds, domain=''):
        """
        :type self: requests.Session
        :param self: 
        :param name: 
        :param value: 
        :param seconds: 
        :return: 
        """
        expires = None
        if seconds:
            d = datetime.datetime.now()
            d += datetime.timedelta(seconds=seconds)
            expires = round((d - datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000)
        self.cookies.set(name, value, domain=domain, path='/', expires=expires)

    def set_incap_cookie(self, v_array, domain=''):
        """

        Translated from:
        ```javascript
        function setIncapCookie(vArray) {
            var res;
            try {
                var cookies = getSessionCookies();
                var digests = new Array(cookies.length);
                for (var i = 0; i < cookies.length; i++) {
                    digests[i] = simpleDigest((vArray) + cookies[i]);
                }
                res = vArray + ",digest=" + (digests.join());
            } catch (e) {
                res = vArray + ",digest=" + (encodeURIComponent(e.toString()));
            }
            createCookie("___utmvc", res, 20);
        }
        ```
        :param v_array: 
        :return: 
        """
        cookies = self.get_session_cookies()
        digests = []
        for cookie_val in cookies:
            digests.append(simple_digest(v_array + cookie_val))
        res = v_array + ',digest=' + ','.join(digests)
        self.create_cookie('___utmvc', res, None, domain=domain)

    def crack(self, resp, org=None, tries=0):
        # Use to hold the original request so that when attempting the new unblocked request, we have a reference
        # to the original url.
        org = org or resp

        # Return original response after too many tries to bypass incap.
        if tries >= self.MAX_INCAP_RETRIES:
            logging.debug('incap blocked. not retrying. {}'.format(resp.url))
            return resp

        # Check for the ROBOTS meta tag in the content.
        # This is a dead giveaway that the resource is blocked by incap.
        soup = BeautifulSoup(resp.content, 'html.parser')
        robots_tag = soup.find('meta', {'name': 'ROBOTS'}) or soup.find('meta', {'name': 'robots'})

        if robots_tag:
            logging.debug('incap blocked. retrying. {}'.format(resp.url))

            # Split the url so that no matter what site is being requested, we can figure out the host of
            # the incapsula resource.
            split = urlsplit(org.url)
            scheme = split.scheme
            host = split.netloc

            # Set cookie then send request to incap resource to "apply" cookie.
            self.set_incap_cookie(test(), host)
            self.get(scheme + '://' + host + '/_Incapsula_Resource?SWKMTFSR=1&e={}'.format(random.random()))

            # Call crack() again since if the request isn't blocked after the above cookie-set and request,
            # then it will just return the unblocked resource.
            return self.crack(self.get(org.url, incap=True), org=org, tries=tries + 1)
        return resp

    def get(self, url, **kwargs):
        r"""Sends a GET request. Returns :class:`Response` object.

        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :param incap: Used so when sending a get request from this instance, we dont end up creating an infinate loop
            by calling .get() then .crack() which calls .get() and repeat x infinity. Also any requests made to get 
            encapsula resources dont need to be cracked.
        :rtype: requests.Response
        """

        kwargs.setdefault('allow_redirects', True)

        # If the request is to get the incapsula resources, then we dont call crack().
        if kwargs.pop('incap', False):
            return self.request('GET', url, **kwargs)

        return self.crack(self.request('GET', url, **kwargs))
