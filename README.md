[![CircleCI](https://circleci.com/gh/ziplokk1/incapsula-cracker-py3.svg?style=shield)](https://circleci.com/gh/ziplokk1/incapsula-cracker-py3)
# Description

This module is used to wrap any request to a webpage blocked by incapsula. Despite the name, this library should be ok to use with python2.7.

Incapsula has begun using re-captcha after too many requests which may seem malicious. As of now, there is no way around it.

Currently in order to detect that, I just simply raise an IncapBlocked error when the page is blocked by re-captcha.

## Documentation can be found [here](https://ziplokk1.github.io/incapsula-cracker-py3/).

# Usage

```python
from incapsula import IncapSession
session = IncapSession()
response = session.get('http://example.com')  # url is not blocked by incapsula
```

```python
# Sometimes incapsula will block based on user agent.
from incapsula import IncapSession
session = IncapSession(user_agent='any-user-agent-string')
respose = session.get('http://example.com')

# This can also be done after instantiation.
session.headers['User-Agent'] = 'some-other-user-agent-string'

# It can also be done on a per request basis, just like requests.
response = session.get('http://example.com', headers={'User-Agent': 'another-user-agent-string'})
```

```python
# Since IncapSession inherits from requests.Session, you can pass all the same arguments to it.
# See the requests documentation here (http://docs.python-requests.org/en/master/user/advanced/#session-objects)
from __future__ import print_function
from incapsula import IncapSession
session = IncapSession()
session.cookies.set('cookie-key', 'cookie-value')
response = session.get('http://example.com', headers={'Referer': 'http://other-example.com'})
print(session.cookies)
```

```python
# Handling re-captcha blocks.
from incapsula import IncapSession, RecaptchaBlocked
session = IncapSession()
try:
    response = session.get('http://example.com')
except RecaptchaBlocked as e:
    raise
```

```python
# Sending a request to a page which is not blocked by incapsula
from incapsula import IncapSession
session = IncapSession()

# When using the bypass_crack param, the IncapSession will not send out extra requests to bypass incapsula.
# This will speed up the requests significantly so if you're making a scraper which
# accesses multiple sites and some don't use incapsula, you can just bypass the crack.
response = session.get('http://example.com', bypass_crack=True)
```

# Setup

`pip install incapsula-cracker-py3`

# Notes

* As of now, this is only proven to work with the following sites:
  * whoscored.com
  * coursehero.com
  * offerup.com
  * dollargeneral.com
* I understand that there's minimal commenting and that's because I'm not sure exactly why incapsula is sending requests to certain pages other than to obtain cookies. This is just a literal reverse engineer of incapsulas javascript code.
* Feel free to contribute. Unfortunately webscraping is such a dynamic field that I can't always put out updates and make changes for specific sites. So I turn to the community to help with those issues. Thank you for your understanding. For anyone who is using this library and it works for your site, please send me a note so i can add it to the list.

# How it works:
Lets start with how incapsula works first:
1. When you navigate to a webpage, incapsula runs some javascript code which tests your browser to see if it's using selenium, phantomJS, mechanize, etc.
2. A cookie is created which holds the results of this test.
3. A request is then sent out which "applies" the cookie and now sends back a few other cookies necessary to obtain access to the site.
4. Any subsequent request is now authorized to access the site until the cookie expires.
5. If there are too many requests being made to the site despite the cookie authentication, incapsula will serve back a re-captcha instead.

When detecting whether a resource is blocked, by default, we look for two elements.

```html
<!-- element 1 -->
<meta name="ROBOTS"/>

<!-- element 2 -->
<iframe src="link to some incapsula resource"></iframe>
```

Finding both of these elements is necessary because unless both tags are present (from what I have seen) then the resource is not blocked.

Once we have determined that the resource is blocked, we send a get request to the `src` of the `iframe` to determine its contents.

If the contents contain a re-captcha, then there's nothing we can do and we raise a `IncapBlocked` exception. Otherwise we set the `___utvmc` cookie, send the GET request to apply the cookie, and send a new request to the original url.


# Customizing
### The iframe src isn't contained in what I have coded already, here is how to expand the list to search.
```html
<head>
    <meta name="ROBOTS"/>
</head>
<body>
    <iframe src="http://some-site-i-havent-added.com"></iframe>
</body>
```
```python
from incapsula import IncapSession, WebsiteResourceParser

class MyResourceParser(WebsiteResourceParser):
    # List of arguments to pass into BeautifulSoup().find() method.
    extra_find_iframe_args = [
        ('iframe', {'src': 'http://some-site-i-havent-added.com'})
    ]

incap_session = IncapSession(resource_parser=MyResourceParser)
# more code here
```
### The resource is blocked by incapsula but there's no `<meta name="ROBOTS"/>` so this library isn't detecting that it's blocked.
```html
<head></head>
<body>
    <iframe src="//content.incapsula.com/jsTest.html"></iframe>
</body>
```
```python
from incapsula import IncapSession, WebsiteResourceParser

class NoRobotsMetaResourceParser(WebsiteResourceParser):
    def is_blocked(self):
        return bool(self.incapsula_iframe)
        
incap_session = IncapSession(resource_parser=NoRobotsMetaResourceParser)
# More code here
```
### The iframe contents have a captcha, but my library isn't detecting that.
```html
<!-- Response from iframe request -->
<body>
    <div class="some-recaptcha-class" id="recaptcha-div">
        <!-- Recaptcha contents -->
    </div>
</body>
```
```python
from incapsula import IncapSession, IframeResourceParser

class MyIframeResourceParser(IframeResourceParser):
    # List of arguments to pass into BeautifulSoup().find() method.
    extra_find_recaptcha_args = [
        ('div', {'class': 'some-recaptcha-class', 'id': 'recaptcha-div'})
    ]
    
incap_session = IncapSession(iframe_parser=MyIframeResourceParser)
```
### Since I've tried to keep this pretty site agnostic, its not always going to work with some sites. I've tried to keep it as extensible as possible so that it's easy to tailor it to a specific site.

## As Always: Scrape responsibly, obey timeouts, and obey the robots.txt. ;)

feel free to contact me at sdscdeveloper@gmail.com
