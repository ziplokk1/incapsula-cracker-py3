# Please Note
## I have not been able to keep this script updated. If there are issues, try to check out the `hotfix` branch and see if that works. 

# Description

This module is used to wrap any request to a webpage blocked by incapsula.

# Usage

## With Requests

```
from incapsula import IncapSession
session = IncapSession()
response = session.get('http://example.com')  # url is not blocked by incapsula
```

# Setup

`pip install incapsula-cracker-py3`

# Notes

* As of now, this is only proven to work with the following sites:
* * whoscored.com
* * coursehero.com
* I understand that there's minimal commenting and that's because I'm not sure exactly why incapsula is sending requests to certain pages other than to obtain cookies. This is just a literal reverse engineer of incapsulas javascript code.
* Feel free to contribute. Unfortunately webscraping is such a dynamic that I can't always put out updates and make changes for specific sites. So I turn to the community to help with those issues. Thank you for your understanding.
