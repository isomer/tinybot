import urllib2
import time
import re

website="pr0nbot.phetast.nu"

def duration(x):
    ret=""
    if x>86400:
        return "%dd%dh%02dm%02ds" % (x/86400,(x/3600)%24,(x/60)%60,x%60)
    if x>3600:
        return "%dh%02dm%02ds" % (x/3600,(x/60)%60,x%60)
    elif x>60:
        return "%dm%02ds" % ((x/60)%60,x%60)
    else:
        return "%ds" % (x%60)

def get_summary(url, page):
	match = re.match("http://pr0nbot.phetast.nu/src/(.*)-([0-9]+)\.jpg$", url)
	if match:
		pagename = urllib2.unquote(urllib2.unquote(match.group(1)))
		pagename = pagename.replace("_"," ").replace("#",": ")
		pagename += " (%s ago)" % duration(time.time()-int(match.group(2)))
		return pagename
	return None
