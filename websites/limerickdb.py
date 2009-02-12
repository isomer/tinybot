import re

website="limerickdb.com"

def get_summary(url, page):
	match = re.match('.*?<div class="quote_output">(.*?)<br />', page, re.DOTALL)

	if match:
		m=match.groups(1)
		firstline = m[0].strip() + "..."
		return firstline
	else:
		return "[limerick]"
