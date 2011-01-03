import re

website="twitter.com"

def get_summary(url, page):

	user = re.match('.*twitter.com/(?:#!/)?([^/]*)(/.*)?', url, re.DOTALL)
	if user:
		user = '@%s' % user.groups(1)[0]
	else:
		user = '<fail whale>'

	match = re.match('.*?<span class="entry-content">(.*?)</span>', page, re.DOTALL)
	if match:
		m = match.groups(1)
		tweet = m[0].strip().replace('</a>', '')
		tweet=re.sub(r'<a [^>]*>', '', tweet)
		return '%s: %s' % (user, tweet)
	else:
		return '[twitter %s]' % user
