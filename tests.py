from __future__ import unicode_literals
import unittest

from incapsula import IncapSession


# ToDo: Test case for when re-captcha is typing the text from the pictures.

# ToDo: Test case for when re-captcha is finding objects in pictures.


class TestIncapBlocked(unittest.TestCase):
    """
    Test case for when the request is blocked by incapsula.
    """
    body = """
    <html style="height:100%"><head><META NAME="ROBOTS" CONTENT="NOINDEX, NOFOLLOW"><meta name="format-detection" content="telephone=no"><meta name="viewport" content="initial-scale=1.0"><meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1"><script type="text/javascript" src="/_Incapsula_Resource?SWJIYLWA=2977d8d74f63d7f8fedbea018b7a1d05"></script></head><body style="margin:0px;height:100%"><iframe src="/_Incapsula_Resource?CWUDNSAI=18&xinfo=10-145639306-0 0NNN RT(1495555623413 147) q(0 -1 -1 -1) r(0 -1) B15(11,4636,0) U5&incident_id=220011010269131805-850355021556761818&edet=15&cinfo=0b000000" frameborder=0 width="100%" height="100%" marginheight="0px" marginwidth="0px">Request unsuccessful. Incapsula incident ID: 220011010269131805-850355021556761818</iframe></body></html>
    """

    def test_incap_blocked(self):
        s = IncapSession()
        self.assertTrue(s.incap_blocked(self.body))


class TestIncapBlockedCheckboxCaptcha(unittest.TestCase):
    """
    Test case for when incapsula is blocked by a checkbox captcha.
    """
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
    def test_incap_recaptcha_blocked(self):
        s = IncapSession()
        self.assertTrue(s.html_is_recaptcha(self.body))