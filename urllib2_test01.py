#!/usr/bin/python

from urllib.request import build_opener
import urllib.request
import urllib.error
from http.cookiejar import CookieJar

cookie = CookieJar()
opener = build_opener(urllib.request.HTTPCookieProcessor(cookie))
req = urllib.request.Request('http://www.baidu.com/')

try: response = opener.open(req)

except urllib.error.URLError as e:
    print(e.code)
    print(e.reason)
    print(type(e.reason))

for i in cookie:
    print('Name = ' + i.name)
    print('Value = ' + i.value)
