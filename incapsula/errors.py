class IncapBlocked(ValueError):
    """
    Base exception for exceptions in this module.

    :param response: The response which was being processed when this error was raised.
    :type response: requests.Response
    :param *args: Additional arguments to pass to :class:`ValueError`.
    """
    def __init__(self, response, *args):
        self.response = response
        super(IncapBlocked, self).__init__(*args)


class MaxRetriesExceeded(IncapBlocked):
    """
    Raised when the number attempts to bypass incapsula has exceeded the amount specified.

    :param response: The response which was being processed when this error was raised.
    :type response: requests.Response
    :param *args: Additional arguments to pass to :class:`ValueError`.
    """
    pass


class RecaptchaBlocked(IncapBlocked):
    """
    Raised when re-captcha is encountered.

    :param response: The response which contains the re-captcha.
    :type response: requests.Response
    :param *args: Additional arguments to pass to :class:`ValueError`.
    """
    pass
