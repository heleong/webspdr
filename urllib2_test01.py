#!/usr/bin/python

import urllib2
import cookielib

cookie = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
#req = urllib2.Request('http://bbs.csdn.net/')
req = urllib2.Request('http://www.baidu.com/')

try: response = opener.open(req)

except urllib2.URLError, e:

    print e.code
    print e.reason
    print type(e.reason)


for i in cookie:
    print 'Name = ' + i.name
    print 'Value = ' + i.value

