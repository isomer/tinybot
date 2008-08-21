import urllib2
import re

website="wikipedia.org"

def get_summary(url, page):
	match = re.match("http://en.wikipedia.org/wiki/(.*)$", url)
	if match:
		pagename = urllib2.unquote(match.group(1))
		pagename = pagename.replace("_"," ").replace("#",": ")
		return pagename
	return None
