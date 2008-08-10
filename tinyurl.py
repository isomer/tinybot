#!/usr/bin/python
import re
import urllib2
import time
import htmlentitydefs
import atom

tinycache={}    # url => tinyurl
summarycache={} # url => summary
timeline={} # channel => tinyurl => (timestamp,who)
realurl={} # tinyurl => url

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
    ret=summarycache[realurl]
    if ret is not None:
        return ret
    else:
        return realurl

def tiny(user,channel,msg):
    if channel not in timeline:
        timeline[channel]={}
    def tinyurl(x):
        print "tinyurling",`x`
        if x in tinycache:
            return tinycache[x]
        if x.startswith("tinyurl.com") \
          or x.startswith("preview.tinyurl.com"):
            realurl[x]=x
            return x
        try:
            f = fetch_url("http://tinyurl.com/create.php?url="+x)
            r = f.read()
            a = re.match('.*href="(http://tiny.*?)"',r, re.DOTALL)
            tinycache[x]=a.groups()[0]
            realurl[a.groups()[0]]=x
        except IOError,e:
            tinycache[x] = e.strerror

        return tinycache[x]

    def findsummary(url):
        """find title or short summary to print next to the url"""
        if url in summarycache:
            return summarycache[url]
        match = re.match("http://en.wikipedia.org/wiki/(.*)$", url)
        if match:
            pagename = urllib2.unquote(match.group(1))
            pagename = pagename.replace("_"," ").replace("#",": ")
            summarycache[url] = pagename
        else:
            try:
                page=fetch_url(url).read(64*1024)
                a = re.match('.*< *title[^>]*>(.*)</ *title *>.*',page, re.DOTALL| re.IGNORECASE)
                if a:
                    summarycache[url]=unhtmlspecialchars(a.group(1).strip())
                    # Apply as many cleanups as possible
                    for s,r in cleanups:
                        summarycache[url] = re.sub(s,r,summarycache[url])
                else:
                    #print "No title tag?",`page`
                    summarycache[url] = None
            except IOError,e:
                summarycache[url] = e.strerror
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
        elif i[1] is not None:
            if i[0] not in timeline[channel]:
                m=m+i[0]+" ["+i[1]+"]"
                timeline[channel][i[0]]=(time.time(),user)
            else:
                m=m+"TIMELINE(%s ago by %s)" % (duration(time.time()-timeline[channel][i[0]][0]),timeline[channel][i[0]][1])
        else:
            if i[0] not in timeline[channel]:
                m=m+i[0]
                timeline[channel][i[0]]=(time.time(),user)
            else:
                m=m+"TIMELINE(%s ago by %s)" % (duration(time.time()-timeline[channel][i[0]][0]),i[0][1])
    if m==origmsg:
        return
    msg="<%s> %s" % (user,m)

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
    atom.generate_atom(channel,atomitems)
        
    return msg


if __name__=="__main__":
    print tiny("me","#channel","http://en.wikipedia.org/wiki/Puppet_state#The_first_puppet_states")
    print tiny("me","#channel","http://pr0nbot.phetast.nu/src/33a44sg-1217237820.jpg")
    print tiny("me","#channel","http://azarask.in/blog/post/not-the-users-fault-manifesto/")
    print tiny("me","#channel","http://slashdot.org this is a test http://example.org http://www.news.com.au/heraldsun/story/0,21985,23245649-5005961,00.html")
    print tiny("me","#channel","http://www.syddutyfree.com.au/ShopNowOrJustBrowsing.aspx?returnURL=%2fcategory%2fliquor%2fwhiskeys-and-cognacs%2f12426-glenfiddich-30-year-old-750ml")
    print tiny("me","#channel","http://foss-means-business.org/Image:IMG_0172.JPG")
    print tiny("me","#channel","http://en.wikipedia.org/wiki/Main_Page")
    print tiny("me","#channel","http://www.trademe.co.nz/Home-living/Lifestyle/Wine-food/Food/auction-165301499.htm")
