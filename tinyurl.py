#!/usr/bin/python
#set encoding=utf-8
import re
import os
import urllib2
import time
import htmlentitydefs
import tempfile

import atom
import websites
import filetypes

tinycache={}    # url => tinyurl
summarycache={} # url => summary
timeline={} # channel => tinyurl => (timestamp,who)
realurl={} # tinyurl => url

debug = False

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

def fetch_url(url):
    """returns a file-like handle that can be read from"""
    u = urllib2.Request(url)
    # wikimedia detects and blocks requests from urllib's default user-agent
    u.add_header('User-Agent','Mozilla/4.0 (compatible; Tinier; Linux; Parsing title tags for IRC)')
    # can add other things to the request before we send it... eg set_proxy()
    u.add_header("Accept","text/html")
    return urllib2.urlopen(u)


def get_real_url(url):
    if url in realurl:
        return realurl[url]
    if "#" in url and url.split("#")[0] in realurl:
        return realurl[url.split("#")[0]]+"#"+url.split("#",1)[1]
    return url

def get_summary(url):
    realurl = get_real_url(url)
    ret = summarycache.get(realurl)
    if ret:
        return ret
    else:
        return realurl

def tiny(user,channel,msg):
    """returns a string to reply to a target, or returns None if there
    was nothing interesting found to reply to in the msg"""
    if channel not in timeline:
        timeline[channel] = {}
    def tinyurl(x):
        """returns the tinied url (and caches it as a side-effect)"""
        print "tinyurling",`x`
        if x in tinycache:
            return tinycache[x]
        if x.startswith("tinyurl.com") \
          or x.startswith("preview.tinyurl.com") or x.startswith("is.gd"):
            realurl[x] = x
            return x
        if not debug:
            try:
                f = fetch_url("http://is.gd/api.php?longurl=" + x.replace("%","%25"))
                r = f.read()
                print "url:",`x`,"tinyurl:",`r`
                tinycache[x] = r
                realurl[r] = x
            except urllib2.HTTPError, e:
                print "tinyurl() HTTP Error %s: %s" % (e.code, e.msg)
            except urllib2.URLError, e:
                # socket.error has .reason -> (int, str)
                print "tinyurl() URLError:", e.reason
            except IOError, e:
                print "tinyurl() IOError:", e.strerror
            except Error, e:
                print "tinyurl() Error: " + str(e)
        if not tinycache.has_key(x): # we had an error above trying to set it
            tinycache[x] = x

        return tinycache[x]

    def findsummary(url):
        """find title or short summary to print next to the url"""
        if url in summarycache:
            return summarycache[url]
        try:
            page = fetch_url(url).read(64*1024)
            summary = websites.get_summary(url, page)
            if summary is None:
                fd, fname = tempfile.mkstemp()
                os.write(fd, page)
                os.close(fd)
                summary = filetypes.get_summary(url, fname)
            if summary and len(summary) > 120:
                # stick to ascii ellipsis for now until the world moves to utf8…
                summary = summary[:120] + '...'
            summarycache[url] = summary
        except IOError, e:
            summarycache[url] = e.strerror
        except Error, e:
            summarycache[url] = str(e)
        return summarycache[url]

    origmsg=msg
    m=""
    bits=[] # msg split up into strings or (tinyurl, summary) items

    while 1:
        a = re.match(r"(.*?)(https?://[-!@a-zA-Z0-9,.%&;=/+:?_~]*[^#\.!,\) ])(#[-!@a-zA-Z0-9,.%&;=/+:?_~]*[^\.!,\) ])?(.*)", msg)
        if a is None:
            if msg: # any trailing text after url
                bits.append(msg)
            break
        starttext, url, frag, msg = a.groups()
        if url.find("tinybot") >= 0:
            # don't allow links to urls related to us - save it
            # to 'bits' as-is
            txt = "".join(map(lambda x:x or "", (starttext, url, frag)))
            bits.append(txt)
            continue
        tinied = tinyurl(url)
        if frag:
            tinied += frag
            url += frag
        if len(tinied) <= len(url): 
            if starttext:
                bits = bits+[starttext]
            bits = bits+[(tinied, findsummary(url))]
        else:
            if starttext:
                bits=bits+[starttext]
            bits=bits+[(url, findsummary(url))]
    m=""
    for i in bits: #(url,summary)
        if type(i)==type(""):
            m=m+i
        elif i[0] not in timeline[channel]:
            timeline[channel][i[0]]=(time.time(),user)
            if i[1] is not None:
                m=m+i[0]+" ["+i[1]+"]"
            else:
                m=m+i[0]
        else:
            m=m+"TIMELINE(%s ago by %s)" % (duration(time.time()-timeline[channel][i[0]][0]),timeline[channel][i[0]][1])
    if m == origmsg:
        return
    msg = "<%s> %s" % (user,m)

    def build_atom_summary(who,url):
        import cgi
        rurl = get_real_url(url).lower()
        if rurl.endswith(".jpg") \
          or rurl.endswith(".jpeg") \
          or rurl.endswith(".png") \
          or rurl.endswith(".gif") \
          :
              html="<img src=\"%s\"/>" % cgi.escape(url)
        else:
            html="<a href=\"%s\">%s</a>" % (
                cgi.escape(get_real_url(url)),
                cgi.escape(get_real_url(url))
                )

        return "&lt;%s&gt; %s" % (who,html)

    atomitems=[]
    for url,(ts,who) in timeline[channel].items():
        atomitems.append(
            (ts,get_summary(url),who,get_real_url(url),url,build_atom_summary(who,url))
            )
    atomitems.sort()
    atomitems.reverse()
    atom.generate_atom(channel,atomitems[:30])
        
    return msg


if __name__=="__main__":
    print tiny("me","#channel","http://pr0nbot.phetast.nu/src/242482_I%2527ve%2520seen%2520these%2520guys%2520before-1220080640.jpg")
    print tiny("me","#channel","http://twitter.com/revgeorge/statuses/884264710")
    print tiny("him","#channel","http://twitter.com/revgeorge/statuses/884264710")
    print tiny("me","#channel","http://en.wikipedia.org/wiki/Puppet_state#The_first_puppet_states")
    print tiny("me","#channel","http://www.stuff.co.nz/4664076a28.html")
    print tiny("me","#channel","http://www.flickr.com/photos/tonyandrach/2712775977/in/set-72157606435991911")
    print tiny("me","#channel","http://porter.net.nz/~alastair/trace.txt")
    print tiny("me","#channel","http://pr0nbot.phetast.nu/src/33a44sg-1217237820.jpg")
    print tiny("me","#channel","http://pr0nbot.phetast.nu/src/33a44sg-1217237820.jpg")
    print tiny("me","#channel","http://azarask.in/blog/post/not-the-users-fault-manifesto/")
    print tiny("me","#channel","http://slashdot.org this is a test http://example.org http://www.news.com.au/heraldsun/story/0,21985,23245649-5005961,00.html")
    print tiny("me","#channel","http://www.syddutyfree.com.au/ShopNowOrJustBrowsing.aspx?returnURL=%2fcategory%2fliquor%2fwhiskeys-and-cognacs%2f12426-glenfiddich-30-year-old-750ml")
    print tiny("me","#channel","http://foss-means-business.org/Image:IMG_0172.JPG")
    print tiny("me","#channel","http://en.wikipedia.org/wiki/Main_Page")
    print tiny("me","#channel","http://www.trademe.co.nz/Home-living/Lifestyle/Wine-food/Food/auction-165301499.htm")

# vi:et:sw=4:ts=4
