import urllib2
import re
import urlparse
try:
	from urlparse import parse_qs
except:
	from cgi import parse_qs
from xml.dom import minidom

website="youtube.com"

def get_summary(url, page):
        o = urlparse.urlparse(url)
        m = parse_qs(o[4])
        v = m['v'][0]
        vurl = "http://gdata.youtube.com/feeds/api/videos/" + v + "?v=2"
        NS = "http://www.w3.org/2005/Atom"
        s = str(urllib2.urlopen(vurl).read())
        us = s.decode('utf-8')
        dom = minidom.parseString(us.encode("utf-8"))
        u = dom.getElementsByTagName('title')[0].firstChild.data
        return u.encode('utf-8')

