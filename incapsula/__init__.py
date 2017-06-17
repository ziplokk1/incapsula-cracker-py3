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


class BaseResourceParser(object):
    """
    Superclass for all other parser objects.
    """

    def __init__(self, response):
        """
        :type response: requests.Response
        :param response:
        """
        self.response = response
        split = urlsplit(response.url)
        self.scheme = split.scheme
        self.host = split.netloc
        self.soup = BeautifulSoup(self.response.content, 'html.parser')


class IframeResourceParser(BaseResourceParser):
    """
    Parser object to obtain the contents of the incapsula iframe.
    """

    def __init__(self, response):
        """

        :param response: The response of the request sent to the incapsula iframe url.
        :type response: requests.Response
        """
        super(IframeResourceParser, self).__init__(response)
        self.recaptcha_elements = [
            ('form', {'id': 'captcha-form'}),
            ('div', {'class': 'g-recaptcha'})
        ]

    def is_recaptcha(self):
        """
        Determine whether the iframe contents is a google recaptcha.

        :return: True if the iframe contains a google recaptcha.
        """
        for element in self.recaptcha_elements:
            if self.soup.find(*element):
                return True
        return False


class WebsiteResourceParser(BaseResourceParser):
    """
    Parser object for the inital resource which was requested.
    """

    def __init__(self, response, extra_iframe_patterns=None):
        """

        :param response: The response of the request sent to the targeted host.
        :param extra_iframe_patterns: A list of compiled regex patterns which will match the incapsula iframe src attribute value.
            Use when there are issues detecting whether the resource is blocked by incapsula.
        :type extra_iframe_patterns: list[_sre.SRE_Pattern]
        """
        super(WebsiteResourceParser, self).__init__(response)
        # Common incapsula iframe src values.
        # Used to find the iframe which hosts the incapsula resource.
        self.incapsula_iframe_src_patterns = [
            re.compile('^/_Incapsula_Resource.*'),
            re.compile('^//content\.incapsula\.com.*')
        ]
        if extra_iframe_patterns:
            self.incapsula_iframe_src_patterns.extend(extra_iframe_patterns)

    @property
    def robots_meta(self):
        """
        The <meta name="ROBOTS"> tag which is so commonly found in incapsula blocked resources.

        :rtype: bs4.element.Tag
        :return:
        """
        return self.soup.find('meta', {'name': re.compile('^robots$', re.IGNORECASE)})

    @property
    def incapsula_iframe(self):
        """
        The iframe which contains the javascript code that runs on browser load.

        :rtype: bs4.element.Tag
        :return:
        """
        for pattern in self.incapsula_iframe_src_patterns:
            iframe = self.soup.find('iframe', {'src': pattern})
            if iframe:
                return iframe

    @property
    def incapsula_iframe_url(self):
        """
        The src attribute value of the incapsula iframe.

        :rtype: str
        :return:
        """
        if self.incapsula_iframe:
            uri = self.incapsula_iframe.get('src')
            # Case when uri isn't actually a uri, but an external resource.
            if uri.startswith('//'):
                return self.scheme + ':' + uri
            return self.scheme + '://' + self.host + uri

    def is_blocked(self):
        """
        Determine whether the resource is blocked by incapsula or not.

        If the resource has the <meta name="ROBOTS"> tag and the incapsula IFrame
        then we can assume the resource is blocked.
        :return:
        """
        return bool(self.robots_meta) and bool(self.incapsula_iframe)


class IncapSession(Session):

    def __init__(self, max_retries=3, user_agent=None, cookie_domain=''):
        """

        :param max_retries: The number of times to attempt to get the incapsula resource before giving up.
            Set this to `None` to never give up.
        :param user_agent: Change the default user agent when sending requests.
        :param cookie_domain: Use this param to change the domain which is set in the cookie.
            Sometimes the domain set for the cookie isn't the same as the actual host. 
            i.e. .domain.com instead of www.domain.com. 
            
        """
        super(IncapSession, self).__init__()

        default_useragent = 'IncapUnblockSession (https://github.com/ziplokk1/incapsula-cracker-py3)'
        user_agent = user_agent or default_useragent

        self.max_retries = max_retries
        self.cookie_domain = cookie_domain
        self.headers['User-Agent'] = user_agent

    def get_incapsula_resource_url(self, scheme, host):
        """
        Override this method to change the get request after the cookies are set.

        After the cookies are set, there is a GET request which must get sent to validate the session.
        Override this method to return a different url to send the GET request to.
        This method is more of a future proofing measure than anything.

        Reverse engineer from:
        ```javascript
        setIncapCookie(test(o));
        document.createElement("img").src = "/_Incapsula_Resource?SWKMTFSR=1&e=" + Math.random()
        ```
        """
        rdm = random.random()
        return scheme + '://' + host + '/_Incapsula_Resource?SWKMTFSR=1&e={}'.format(rdm)

    def get_session_cookies(self):
        """
        Get a list of cookies which start with 'incap_ses_'.
        
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
        return [cookie.value for cookie in self.cookies if cookie.name.startswith('incap_ses_')]

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

    def raise_for_recaptcha(self, resource):
        """
        Raise an IncapBlocked exception if the iframe in the original resource contains a recaptcha.

        Send get request to iframe url to get the contents and raise if the contents contain a re-captcha.

        :param resource: Resource object from original request.
        :return:
        """
        # Get the content from the iframe.
        iframe_response = self.get(resource.incapsula_iframe_url, bypass_crack=True)
        iframe_resource = IframeResourceParser(iframe_response)

        if iframe_resource.is_recaptcha():
            raise IncapBlocked(iframe_response, 'resource blocked by re-captcha')

    def apply_cookies(self, original_url):
        """
        Set the session cookies and send the necessary GET request to "apply" the cookies.

        :param original_url: The url of the original request.
            Needed to determine the scheme and host of the domain to send the request to apply the cookies.
        :return:
        """
        # Split the url so that no matter what site is being requested, we can figure out the host of
        # the incapsula resource.
        split = urlsplit(original_url)
        scheme = split.scheme
        host = split.netloc

        # Set the cookie then send request to incap resource to "apply" cookie.
        self.set_incap_cookie(test(), self.cookie_domain or host)
        self.get(self.get_incapsula_resource_url(scheme, host), bypass_crack=True)

    def crack(self, resp, org=None, tries=0):
        """
        If the response is blocked by incapsula then set the necessary cookies and attempt to bypass it.

        :param resp: Response to check.
        :param org: Original response. Used only when called recursively.
        :param tries: Number of attempts. Used only when called recursively.
        :return:
        """
        # Use to hold the original request so that when attempting the new unblocked request, we have a reference
        # to the original url.
        org = org or resp

        # Return original response after too many tries to bypass incap.
        # If max_retries is None then this part will never get executed allowing a continuous retry.
        if self.max_retries is not None and tries >= self.max_retries:
            raise IncapBlocked(resp, 'max retries exceeded when attempting to crack incapsula')

        resource = WebsiteResourceParser(resp)
        if resource.is_blocked():
            logger.debug('Resource is blocked. attempt={} url={}'.format(tries, resp.url))
            # Raise if the response content's iframe contains a recaptcha.
            self.raise_for_recaptcha(resource)

            # Apply cookies and send GET request to apply them.
            self.apply_cookies(org.url)

            # Recursively call crack() again since if the request isn't blocked after the above cookie-set and request,
            # then it will just return the unblocked resource.
            return self.crack(self.get(org.url, bypass_crack=True), org=org, tries=tries+1)

        return resp

    def get(self, url, bypass_crack=False, **kwargs):
        """
        Sends a GET request. Returns :class:`Response` object.
        
        :param url: URL for the new :class:`Request` object.
        :param bypass_crack: Use when sending a request that you dont want to go through the incapsula crack.
        :param kwargs: Optional arguments that ``request`` takes.
            Used in this class so when sending a get request from this instance,
            we dont end up creating an infinate loop by calling .get() then .crack() which calls .get()
            and repeat x infinity. Also any requests made to get incapsula resources don't need to be cracked.
        :rtype: requests.Response
        """

        kwargs.setdefault('allow_redirects', True)

        # If the request is to get the incapsula resources, then we dont call crack().
        if bypass_crack:
            return self.request('GET', url, **kwargs)

        return self.crack(self.request('GET', url, **kwargs))
