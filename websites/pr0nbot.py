import urllib2
import time
import re

website="pr0nbot.phetast.nu"

def when(t):
    diff = time.time()-t
    ret=""
    if diff>86400*30:
    	return time.strftime("%Y-%m-%d",time.localtime(t))
    elif diff>86400*7:
        return time.strftime("%a %B %d",time.localtime(t))
    elif diff>86400*2:
    	return "last "+time.strftime("%A",time.localtime(t))
    elif diff>86400:
    	return "yesterday"
    elif diff>3600:
        return "%d hours, %d minutes ago" % (diff/3600,(diff/60)%60)
    elif diff>60:
        return "%d minutes, %d seconds ago" % ((diff/60)%60,diff%60)
    else:
        return "%d seconds ago" % (diff%60)

def get_summary(url, page):
	match = re.match("(?i)https?://pr0nbot.phetast.nu/src/(.*)-([0-9]+)\.(gif|jpe?g|png)$", url)
	if match:
		pagename = urllib2.unquote(urllib2.unquote(match.group(1)))
		pagename = pagename.replace("_"," ").replace("#",": ")
		pagename += " (%s)" % when(int(match.group(2)))
		return pagename
	return None
