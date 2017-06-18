import re
from six.moves.urllib.parse import urlsplit

from bs4 import BeautifulSoup


class ResourceParser(object):
    """
    Superclass for all other parser objects.

    :param response: Response from GET request.
    :type response: requests.Response
    """

    def __init__(self, response):
        """
        :param response: Response from GET request.
        :type response: requests.Response
        """
        self.response = response
        split = urlsplit(response.url)
        self.scheme = split.scheme
        self.host = split.netloc
        self.soup = BeautifulSoup(self.response.content, 'html.parser')

    def is_blocked(self):
        """
        Override this method to determine whether or not the resource is blocked.

        .. note:: If this class is passed into :class:`IncapSession` as the ``resource_parser`` parameter then this
            method will be used to determine whether to attempt to bypass incapsula or raise
            a :class:`MaxRetriesExceeded` error on too many retries.

        .. note:: If this class is passed into :class:`IncapSession` as the ``iframe_parser`` parameter then
            this method will be used to determine whether to raise a :class:`RecaptchaBlocked` error when a
            re-captcha is encountered.

        :return: True if resource is blocked otherwise False
        """
        raise NotImplementedError('`is_blocked()` is not implemented')


class IframeResourceParser(ResourceParser):
    """
    Parser object to obtain the contents of the incapsula iframe.

    :param response: The response of the request sent to the incapsula iframe url.
    :type response: requests.Response
    """

    # Standard args to use with soup.find() when searching for the element which contains a recaptcha.
    default_find_recaptcha_args = [
        ('form', {'id': 'captcha-form'}),
        ('div', {'class': 'g-recaptcha'})
    ]

    # Extra find recaptcha args to use when subclassing.
    # Note: when searching for the recaptcha, it will search for the recaptcha using the values in this list first then
    # it will search using the default_find_iframe_args list.
    extra_find_recaptcha_args = []

    def __init__(self, response):
        """

        :param response: The response of the request sent to the incapsula iframe url.
        :type response: requests.Response
        """
        super(IframeResourceParser, self).__init__(response)

    @property
    def recaptcha_element(self):
        """
        Recaptcha element in the document.

        :rtype: bs4.element.Tag
        """
        # Iterate over user defined list first.
        for element in self.extra_find_recaptcha_args:
            elem = self.soup.find(*element)
            if elem:
                return elem
        # Then iterate over defaults.
        for element in self.default_find_recaptcha_args:
            elem = self.soup.find(*element)
            if elem:
                return elem

    def is_blocked(self):
        """
        Determine whether the iframe contents is a google recaptcha.

        This is determined by simply iterating over the combined results of default_find_recaptcha_args and
        extra_find_recaptcha_args then seeing if the element is found in the document.

        :return: True if the iframe contains a google recaptcha.
        :rtype: bool
        """
        return bool(self.recaptcha_element)


class WebsiteResourceParser(ResourceParser):
    """
    Parser object to extract the robots meta element, incapsula iframe element, and the incapsula iframe url.

    :param response: The response of the request sent to the targeted host.
    :type response: requests.Response
    """

    # Standard args to use with soup.find() when searching for the iframe.
    default_find_iframe_args = [
        ('iframe', {'src': re.compile('^/_Incapsula_Resource.*')}),
        ('iframe', {'src': re.compile('^//content\.incapsula\.com.*')})
    ]

    # Extra find iframe args to use when subclassing.
    # Note: when searching for the iframe, it will search for the iframe using the values in this list first then
    # it will search using the default_find_iframe_args list.
    extra_find_iframe_args = []

    def __init__(self, response):
        """

        :param response: The response of the request sent to the targeted host.
        :type response: requests.Response
        """
        super(WebsiteResourceParser, self).__init__(response)

    @property
    def robots_meta(self):
        """
        The meta robots tag which is so commonly found in incapsula blocked resources.

        :rtype: bs4.element.Tag
        """
        return self.soup.find('meta', {'name': re.compile('^robots$', re.IGNORECASE)})

    @property
    def incapsula_iframe(self):
        """
        The iframe which contains the javascript code that runs on browser load.

        :rtype: bs4.element.Tag
        """
        # Iterate over user defined args first.
        for element in self.extra_find_iframe_args:
            iframe = self.soup.find(*element)
            if iframe:
                return iframe
        # Then iterate over defaults.
        for element in self.default_find_iframe_args:
            iframe = self.soup.find(*element)
            if iframe:
                return iframe

    @property
    def incapsula_iframe_url(self):
        """
        The src attribute value of the incapsula iframe.

        :rtype: str
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

        :return: True if the robots meta tag and the incapsula iframe are both found in the document.
        :rtype: bool
        """
        return bool(self.robots_meta) and bool(self.incapsula_iframe)
