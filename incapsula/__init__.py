import datetime
from urllib import parse
import logging

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
    r = [parse.quote('='.join(x), safe='()') for x in o]
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
        self.headers[
            'User-Agent'] = 'IncapUnblockSession (sdscdeveloper@gmail.com | https://gist.github.com/ziplokk1/a158e2d7dbc2eac998942219325d7674)'

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
        org = org or resp
        if tries >= self.MAX_INCAP_RETRIES:
            logging.warning('incap blocked. not retrying. {}'.format(resp.url))
            return resp
        if resp.status_code == 403:
            logging.warning('incap blocked. retrying. {}'.format(resp.url))
            self.set_incap_cookie(test(), parse.urlsplit(org.url).netloc)
            return self.crack(self.get(org.url, incap=True), org=org, tries=tries + 1)
        return resp

    def get(self, url, **kwargs):
        r"""Sends a GET request. Returns :class:`Response` object.

        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """

        kwargs.setdefault('allow_redirects', True)
        if kwargs.pop('incap', False):
            return self.request('GET', url, **kwargs)
        return self.crack(self.request('GET', url, **kwargs))
