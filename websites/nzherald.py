import re

website="nzherald.co.nz"

def get_summary(url, page):
	"nzherald.co.nz summary generator - remove boilerplate from title tag"
	title = None
	match = re.match(".*<title>(.*?)</title>", page, re.DOTALL)
	if match:
		title = match.group(1)
		# keep text up until date string
		match = re.match("(.*) - \d+ [A-Z][a-z]{2} 20\d\d", title)
		if match:
			title = match.group(1)
	return title
