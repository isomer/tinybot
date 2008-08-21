import re

website="flickr.com"

def get_summary(url, page):
	match = re.match(".*<h1.*>(.*)</h1>.*Uploaded on <a.*>(.*)</a>.*by <a.*><b>(.*)</b></a>.*", page,re.DOTALL)
	if match:
		m=match.groups(1)
		name=m[0]
		date=m[1]
		by=m[2]
		return "Flickr: "+name+" by "+by+" ("+date+")"
	else:
		return "can't find"
