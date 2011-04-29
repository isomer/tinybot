import re

website="stuff.co.nz"

def get_summary(url, page):
	"stuff.co.nz summary generator - removes boilerplate from title"
	title = None
	# get header
	match = re.match(".*?<h1>(.*?)</h1>", page,re.DOTALL)
	if match:
		title = match.group(1)
	else:
		match = re.match(".*<title>(.*?)</title>", page, re.DOTALL)
		if match:
			title = match.group(1).strip()
			# keep text up until date string
			match = re.match("(.*?) - New Zealand", title)
			print title, match
			if match:
				title = match.group(1)
	# remove any html tags (eg for "BREAKING NEWS")
	title, count = re.subn('<[^>]+>', '', title)
	return title.strip()
