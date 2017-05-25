# Description

This module is used to wrap any request to a webpage blocked by incapsula. Despite the name, this library should be ok to use with python2.7.

Encapsula has begun using re-captcha after too many requests which may seem malicious. As of now, there is no way around it.

Currently in order to detect that, I just simply raise an IncapBlocked error when the page is blocked by re-captcha.

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
from incapsula import IncapSession, IncapBlocked
session = IncapSession()
try:
    response = session.get('http://example.com')
except IncapBlocked as e:
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

## As Always: Scrape responsibly, obey timeouts, and obey the robots.txt. ;)

feel free to contact me at sdscdeveloper@gmail.com
