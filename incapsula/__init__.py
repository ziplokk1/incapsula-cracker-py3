from __future__ import unicode_literals

import datetime
import logging
import random

import re
from six.moves.urllib.parse import quote, urlsplit

from bs4 import BeautifulSoup
from requests import Session

logger = logging.getLogger('incapsula')


class IncapBlocked(ValueError):

    def __init__(self, response, *args):
        self.response = response
        super(IncapBlocked, self).__init__(*args)


# A list of valid values which are tested in the incapsula test method.
# These values are pulled straight from my browser and should be enough to spoof
# the robot check when setting the cookie.
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
    """
    Quote each value in the tuple list and return a comma delimited string of the parameters.
    
    This method is a shortened version of incapsulas test method. What the original method does is check 
    for specific plugins in your browser and set a cookie based on which extensions you have installed.
    The list of the values is taken from my own browser after running the test method so they are all valid.
    
    This is just more of a shortcut method instead of trying to reverse engineer the entire code that they had.
    :return: 
    """
    # safe param set to () for the single parameter with the key of "eval.toString().length".
    # This is needed to match the cookie value exactly with what is expected from incapsula.
    r = [quote('='.join(x), safe='()') for x in o]
    return ','.join(r)


def simple_digest(s):
    """
    Create a sum of the ordinal values of the characters passed in from s.

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
    :param s: The string to calculate the digest from.
    :return: 
    """
    res = 0
    for ch in s:
        res += ord(ch)
    return str(res)


class IncapSession(Session):
    # Max retries before giving up cracking incapsula.
    MAX_INCAP_RETRIES = 3
    # noinspection PyPep8
    default_useragent = 'IncapUnblockSession (sdscdeveloper@gmail.com | https://github.com/ziplokk1/incapsula-cracker-py3)'

    def __init__(self, **kwargs):
        # noinspection PyPep8
        """
                
        :param kwargs: 
        :param user_agent: Change the default user agent when sending requests.
        :param cookie_domain: Use this param to change the domain which is set in the cookie.
            Sometimes the domain set for the cookie isn't the same as the actual host. 
            i.e. .domain.com instead of www.domain.com. 
            
        """
        user_agent = kwargs.pop('user_agent', self.default_useragent)
        self.cookie_domain = kwargs.pop('cookie_domain', '')
        super(IncapSession, self).__init__()
        self.headers['User-Agent'] = user_agent

    def get_session_cookies(self):
        """
        Get cookies from the session to use with set_incap_cookie.
        
        Needed to create the simple_digest for the final cookie later.

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
        Set the incapsula cookie in the session cookies.
        
        :param domain: 
        :param name: Cookie name.
        :param value: Cookie value.
        :param seconds: Expiry seconds from the current time.
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
        Calculate the final value for the cookie needed to bypass incapsula.
        
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
        :param domain: 
        :param v_array: 
        :return: 
        """
        cookies = self.get_session_cookies()
        digests = []
        for cookie_val in cookies:
            digests.append(simple_digest(v_array + cookie_val))
        res = v_array + ',digest=' + ','.join(digests)
        logger.debug('setting ___utmvc cookie to {}'.format(res))
        self.create_cookie('___utmvc', res, 20, domain=domain)

    # noinspection PyMethodMayBeStatic
    def incap_blocked(self, content):
        """
        Check if the resource is blocked by incapsula.
        
        :param content: HTML string.
        :return: 
        """
        # Check for the ROBOTS meta tag in the content.
        # This is a dead giveaway that the resource is blocked by incap.
        soup = BeautifulSoup(content, 'html.parser')
        # Not always reliable since some pages have a <meta name="robots"> even if its not blocked by incap.
        # To circumvent that, we also look for an iframe which shows the incapsula error message.
        robots_tag = soup.find('meta', {'name':  re.compile('^robots$', re.IGNORECASE)})
        incap_iframe = soup.find('iframe', {'src': re.compile('^/_Incapsula_Resource.*')})
        return robots_tag and incap_iframe

    def html_is_recaptcha(self, html_string):
        """
        Check if the html contains recaptcha robot prevention.
        
        :param html_string: 
        :return: 
        """
        soup = BeautifulSoup(html_string, 'html.parser')
        return bool(soup.find('form', {'id': 'captcha-form'}) or soup.find('div', {'class': 'g-recaptcha'}))

    def incap_recaptcha_blocked(self, scheme, host, content):
        """
        Get the content from the iframe in a blocked request to determine if the block contains a captcha.
        
        :param scheme: http, ftp, https, etc.
        :param host: www.example.com.
        :param content: HTML content from a response.
        :return: 
        """
        soup = BeautifulSoup(content, 'html.parser')
        # Get incap iframe
        incap_iframe = soup.find('iframe', {'src': re.compile('^/_Incapsula_Resource.*')})
        # If the iframe doesn't exist then it's not recaptcha blocked.
        if not incap_iframe:
            return False

        # Send request to get the content of the iframe.
        iframe_url = incap_iframe.get('src')
        resource = self.get(scheme + '://' + host + iframe_url, bypass_crack=True)

        # If the below method is true, then the iframe content is for a recaptcha and there's no way around that.
        return self.html_is_recaptcha(resource.content)

    def crack(self, resp, org=None, tries=0):
        # Use to hold the original request so that when attempting the new unblocked request, we have a reference
        # to the original url.
        org = org or resp

        # Return original response after too many tries to bypass incap.
        if tries >= self.MAX_INCAP_RETRIES:
            raise IncapBlocked(resp, 'max retries exceeded when attempting to crack incapsula.')

        if self.incap_blocked(resp.content):
            logger.debug('incap blocked. attempt={} url={}'.format(tries, resp.url))

            # Split the url so that no matter what site is being requested, we can figure out the host of
            # the incapsula resource.
            split = urlsplit(org.url)
            scheme = split.scheme
            host = split.netloc

            if self.incap_recaptcha_blocked(scheme, host, resp.content):
                raise IncapBlocked(resp, 'resource blocked by incapsula re-captcha method.')

            # Set cookie then send request to incap resource to "apply" cookie.
            self.set_incap_cookie(test(), self.cookie_domain or host)
            self.get(scheme + '://' + host + '/_Incapsula_Resource?SWKMTFSR=1&e={}'.format(random.random()))

            # Call crack() again since if the request isn't blocked after the above cookie-set and request,
            # then it will just return the unblocked resource.
            return self.crack(self.get(org.url, bypass_crack=True), org=org, tries=tries+1)
        return resp

    # noinspection PyIncorrectDocstring
    def get(self, url, **kwargs):
        """
        Sends a GET request. Returns :class:`Response` object.
        
        :param url: URL for the new :class:`Request` object.
        :param kwargs: Optional arguments that ``request`` takes.
        :param kwargs['bypass_crack']: Use when sending a request that you dont want to go through the incapsula crack.
            Used in this class so when sending a get request from this instance, 
            we dont end up creating an infinate loop by calling .get() then .crack() which calls .get()
            and repeat x infinity. Also any requests made to get encapsula resources dont need to be cracked.
        :rtype: requests.Response
        """

        kwargs.setdefault('allow_redirects', True)

        # If the request is to get the incapsula resources, then we dont call crack().
        if kwargs.pop('bypass_crack', False):
            return self.request('GET', url, **kwargs)

        return self.crack(self.request('GET', url, **kwargs))
