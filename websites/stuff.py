import re

website="stuff.co.nz"

def get_summary(url, page):
	print "stuff.co.nz summary generator"
	match = re.match(".*<p><strong>(.*)</strong></p>.*", page,re.DOTALL)
	if match:
		return match.groups(1)[0]
	else:
		return "can't find"
