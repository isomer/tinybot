import re

website="twitter.com"

def get_summary(url, page):
	match = re.match('.*?<div class="desc">\s*<p>(.*?)</p>', page, re.DOTALL)

	if match:
		m=match.groups(1)
		tweet = m[0].strip()
		return tweet
	else:
		return "[twitter]"
