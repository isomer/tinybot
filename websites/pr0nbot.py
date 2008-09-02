import urllib2
import time
import re

website="pr0nbot.phetast.nu"

def when(x):
    ret=""
    if x>86400*30:
    	return time.strftime("%Y-%m-%d",time.localtime(x))
    elif x>86400*7:
        return time.strftime("%a %B %d",time.localtime(x))
    elif x>86400*2:
    	return "last "+time.strftime("%A",time.localtime(x))
    elif x>86400:
    	return "yesterday"
    elif x>3600:
        return "%d hours, %d minutes ago" % (x/3600,(x/60)%60)
    elif x>60:
        return "%d minutes, %d seconds ago" % ((x/60)%60,x%60)
    else:
        return "%d seconds ago" % (x%60)

def get_summary(url, page):
	match = re.match("(?i)http://pr0nbot.phetast.nu/src/(.*)-([0-9]+)\.(gif|jpe?g)$", url)
	if match:
		pagename = urllib2.unquote(urllib2.unquote(match.group(1)))
		pagename = pagename.replace("_"," ").replace("#",": ")
		pagename += " (%s)" % when(time.time()-int(match.group(2)))
		return pagename
	return None
