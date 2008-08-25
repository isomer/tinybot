import glob
import re
import htmlentitydefs

summary_generators={}

cleanups = [
    (r"\n",r" "),
    (r"\r",r" "),
    (r"YouTube - (.*)",r"\1"),
    (r"(.*) - NZ Herald.*",r"\1"),
    (r"Slashdot \| (.*)",r"\1"),
    (r"(.*) \| NEWS.com.au",r"\1"),
    (r"(.*) - Yahoo! News",r"\1"),
    (r"(.*) - TradeMe.co.nz - New Zealand",r"\1"),
    (r"(.*) *- New Zealand's source for.* on Stuff.co.nz}",r"\1"),
]


for file in glob.glob("websites/*.py"):
	if not file.endswith("__init__.py"):
		x = __import__(file[:-2])
		if "get_summary" in dir(x) and "website" in dir(x):
			summary_generators[x.website]=x.get_summary

def get_summary(url, page):
	match = re.match("https?://([^/]+)", url, flags=re.IGNORECASE)
	if not match:
		return None
	domain = match.group(1)
	#print "summary for",domain
	if domain in summary_generators:
		return summary_generators[domain](url, page)
	while 1:
		parts = domain.split(".")
		parts.pop(0)
		if len(parts) == 0:
			break
		domain = ".".join(parts)
		#print "failed, now summary for",domain
		if domain in summary_generators:
			return summary_generators[domain](url, page)

		a = re.match('.*< *title[^>]*>(.*)</ *title *>.*',page, re.DOTALL| re.IGNORECASE)
		if a:
			title=unhtmlspecialchars(a.group(1).strip())
			# Apply as many cleanups as possible
			for s,r in cleanups:
				title = re.sub(s,r,title)
		else:
			title=None
		return title

def unhtmlspecialchars(x):
    "Remove &entities; from HTML"
    ret=u""
    x=x.decode("utf8")
    while 1:
        s = re.match("(.*?)&(#?[A-Za-z0-9]+);(.*)",x)
        if not s:
            return (ret+x).encode("utf8")
        lhs,entity,rhs = s.groups()
        if entity.startswith("#"):
            ret=ret+lhs+unichr(int(entity[1:]))
        else:
            ret=ret+lhs+htmlentitydefs.entitydefs[entity].decode("latin1")
        x=rhs

