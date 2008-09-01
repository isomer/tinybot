import re

website="flickr.com"

def clean(html):
	"""strip html tags etc"""
	txt = re.sub('<[^>]+>', '', html)
	txt = txt.replace('&nbsp;', ' ').strip()
	return txt

def get_summary(url, page):
	heading, date, by = None, None, ""

	# try getting first heading tag in the Main div
	index = page.find('<div id="Main')
	if index > -1:
		# take stuff between first heading tag in the Main div
		match = re.match(r".*?<h(\d)[^>]*>(.*?)</h\1>", page, re.DOTALL)
		if match:
			# remove html tags and extraneous whitespace
			heading = clean(match.group(2))

	index = page.find('Uploaded on')
	if index > -1:
		match = re.match("Uploaded on <a[^>]*>(.*?)</a>(.*?)</div>", page[index:], re.DOTALL)
		if match:
			date = match.group(1)
			# remove html tags and extraneous whitespace
			leftover = clean(match.group(2))
			if leftover.startswith("by "):
				by = leftover[3:]

	title = ""
	if heading:
		title = "Flickr: " + heading
	if by:	
		title += " by " + by
	if date:
		title += " (%s)" % date
	return title	
