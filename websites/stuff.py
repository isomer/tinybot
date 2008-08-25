import re

website="stuff.co.nz"

def get_summary(url, page):
	"stuff.co.nz summary generator - removes boilerplate from title"
	title = None
	# get bolded first sentence instead
	match = re.match(".*?<p><strong>(.*?)</strong></p>", page,re.DOTALL)
	if match:
		title = match.group(1)
		return title
	match = re.match(".*<title>(.*?)</title>", page, re.DOTALL)
	if match:
		title = match.group(1).strip()
		# keep text up until date string
		match = re.match("(.*?) - New Zealand", title)
		print title, match
		if match:
			title = match.group(1)
	return title
