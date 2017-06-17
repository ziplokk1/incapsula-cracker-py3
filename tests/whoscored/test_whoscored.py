from __future__ import absolute_import

import os
import unittest

from bs4 import BeautifulSoup

from incapsula import WebsiteResourceParser, IframeResourceParser
from tests.helpers import make_response


test_root = os.path.dirname(os.path.abspath(__file__))
blocked_index = os.path.join(test_root, 'index.html')
unblocked_index = os.path.join(test_root, 'whoscored-index_unblocked.html')
iframe = os.path.join(test_root, 'jsTest.html')


class TestWhoScoredIndexBlocked(unittest.TestCase):

    def setUp(self):
        with open(blocked_index, 'rb') as f:
            content = f.read()
        self.parser = WebsiteResourceParser(make_response('http://whoscored.com', content))

    def test_robots_meta(self):
        robots_meta = BeautifulSoup('<META NAME="robots" CONTENT="noindex,nofollow">', 'html.parser').find('meta')
        self.assertEqual(self.parser.robots_meta, robots_meta)

    def test_incapsula_iframe(self):
        incapsula_iframe = BeautifulSoup('<iframe style="display:none;visibility:hidden;" src="//content.incapsula.com/jsTest.html" id="gaIframe"></iframe>', 'html.parser').find('iframe')
        self.assertEqual(self.parser.incapsula_iframe, incapsula_iframe)

    def test_incapsula_iframe_url(self):
        url = 'http://content.incapsula.com/jsTest.html'
        self.assertEqual(self.parser.incapsula_iframe_url, url)

    def test_is_blocked(self):
        self.assertTrue(self.parser.is_blocked())


class TestWhoScoredIndexUnblocked(unittest.TestCase):

    def setUp(self):
        with open(unblocked_index, 'rb') as f:
            content = f.read()
        self.parser = WebsiteResourceParser(make_response('http://whoscored.com', content))

    # We don't care about whether the iframe or robots tag exist in this case as long as is_blocked is false.

    def test_is_blocked(self):
        self.assertFalse(self.parser.is_blocked())


class TestWhoScoredIframeContentsNoRecaptcha(unittest.TestCase):

    def setUp(self):
        with open(iframe, 'rb') as f:
            content = f.read()
        self.parser = IframeResourceParser(make_response('http://content.incapsula.com/jsTest.html', content))

    def test_is_recaptcha(self):
        self.assertFalse(self.parser.is_recaptcha())
