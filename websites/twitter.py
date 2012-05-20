import re
import urllib2
import json

website="twitter.com"

def get_summary(url, page):

    user = re.match('.*twitter.com/(?:#!/)?([^/]*)(/.*)?', url, re.DOTALL)
    if user:
        user = '@%s' % user.groups(1)[0]
    else:
        user = '<fail whale>'

    urlparts = url.split("/")
    if urlparts[-2] == "status":
        tweetid = urlparts[-1]
        url = "https://api.twitter.com/1/statuses/show.json?id=%s" % tweetid
        d = urllib2.urlopen(url).read()
        data = json.loads(d)
        return data["text"].encode("ascii", "ignore")
    else:
        u = user[1:]
        url = "https://api.twitter.com/1/users/lookup.json?screen_name=%s" % u
        d = urllib2.urlopen(url).read()
        data = json.loads(d)
        return data[0]["status"]["text"].encode("ascii", "ignore")
