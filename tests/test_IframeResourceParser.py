import unittest

from tests.helpers import make_response
from incapsula import IframeResourceParser


class TestIframeResourceParserReCaptcha(unittest.TestCase):

    body = """
    <div class="container">
        <div class="container-inner">
            <div class="main">
                <div class="main-inner">
                    <div class="error-headline">
                        <div class="headline-inner">
                            <h1>dollargeneral.com -</h1>
                            <p>Additional security check is required</p>
                        </div>
                    </div>
                    <div class="error-content">
                        <div class="captcha">
                            <div class="form_container">
                                <div class="g-recaptcha" data-sitekey="6Ld38BkUAAAAAPATwit3FXvga1PI6iVTb6zgXw62" data-callback="onCaptchaFinished" ></div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="powered-by">
                    <span class="text">Powered by</span>
                    <a href="//www.incapsula.com/why-am-i-seeing-this-page.html?src=23&amp;utm_source=blockingpages" target="_blank" class="copyrights">Incapsula</a>
                </div>

                <div class="info-text">
                    <strong>What is this page?</strong>
                    <p>The web site you are visiting is protected and accelerated by Incapsula. Your computer might have been infected by some kind of malware and flagged by Incapsula network. This page is presented by Incapsula to verify that a human is behind the traffic to this site and not malicious software.</p>

                    <strong>What should i do?</strong>
                    <p>Simply enter the two words in the image above to pass the security check, once you do that we will remember your answer and will not show this page again. You should run a virus and malware scan on your computer to remove any infection.</p>
                </div>
            </div>
        </div>
    </div>
    """

    def setUp(self):
        self.parser = IframeResourceParser(make_response('http://dollargeneral.com/iframe-fake-url', self.body))

    def test_is_recaptcha(self):
        self.assertTrue(self.parser.is_recaptcha())
