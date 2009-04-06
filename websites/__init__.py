#set encoding=utf-8
import sys
import glob
import re
import htmlentitydefs
import signal

"""this module dynamically loads all the other modules for handling
urls from specific domain names, and also provides a default handler.
This module will re-load all the plugin module when the process receives
a USR1 signal."""

summary_generators = {}

cleanups = [
    ("\r|\n", " "),
    ("YouTube - (.*)", r"\1"),
    (r"Slashdot \| (.*)", r"\1"),
    (r"(.*) \| NEWS.com.au", r"\1"),
    ("(.*) - Yahoo! News", r"\1"),
    ("(.*) - TradeMe.co.nz - New Zealand", r"\1"),
]

def load_plugins():
    """load each website-specific parser"""
    print >>sys.stderr, "loading website plugins:"
    for filename in glob.glob("websites/*.py"):
        if not filename.endswith("__init__.py"):
            try:
                module_name = filename[:-3]
                if sys.modules.has_key(module_name): # previously loaded
                    del(sys.modules[module_name]) # forget it's loaded
                x = __import__(module_name)
                if "get_summary" in dir(x) and "website" in dir(x):
                    summary_generators[x.website] = x.get_summary
                    print >>sys.stderr, "loaded handler for %s" % x.website
            except Exception, e:
                print >>sys.stderr, "error loading %s:" % filename, e

def get_summary(url, page):
    title = None
    match = re.match("https?://([^/]+)", url, flags=re.IGNORECASE)
    if not match:
        return None
    domain = match.group(1)

    # see if we have a specific handler for this domain
    while True:
        if domain in summary_generators:
            try:
                title = summary_generators[domain](url, page)
            except Exception, e:
                print >>sys.stderr, "get_summary for %url failed:" % url, e
            break
        # didn't have a handler for this domain... try removing subdomains
        dotpos = domain.find('.')
        if dotpos == -1: # no more domains to try
            break
        domain = domain[dotpos+1:]

    if not title: # no specific handler found
        a = re.match('.*?< *title[^>]*>(.*?)</ *title *>.*',page, re.DOTALL| re.IGNORECASE)
        if a:
            title = a.group(1)
    if title:
        # remove entities
        title = unhtmlspecialchars(title)
        # Apply as many cleanups as possible
        for rx, replacement in cleanups:
            title = re.sub(rx, replacement, title)
        # remove leading/trailing whitespace
        title = title.strip()
    return title

def unhtmlspecialchars(txt):
    "Remove &entities; from HTML"
    txt = txt.decode("utf8") # turn into a unicode str
    def get_entity_char(match):
        """returns a unicode encoded char string for a given html entity
        (eg '&#167;' -> u'§', '&eacute;' -> u'é') """
        entity = match.group(1)
        if not entity.startswith("&#"):
            # it's a named entity
            try:
                entity = htmlentitydefs.entitydefs[entity[1:-1]].decode("latin1")
            except:
                # someone has used a non-standard entity name, or made a typo?
                pass
            # we now either have a unicode char, or another html entity if
            # it was a char not in latin1...
        if entity.startswith("&#"):
            # Numeric Character Reference
            code = entity[2:-1] # ignore leading &# and trailing ;
            if code[0] in ('x','X'): # hex
                return unichr(int(code[1:], 16))
            return unichr(int(code))
        return entity

    ret = re.sub("(&#?[A-Za-z0-9]+;)", get_entity_char, txt)
    return ret.encode('utf8')

load_plugins()

cur_usr1_handler = signal.getsignal(signal.SIGUSR1)
if cur_usr1_handler in (signal.SIG_IGN, signal.SIG_DFL, None):
    new_handler = lambda sig, stack: load_plugins()
else:
    # chain onto the end of the current handler
    new_handler = lambda sig, stack: cur_usr1_handler() and load_plugins()
signal.signal(signal.SIGUSR1, new_handler)

# vi:et:ts=4:sw=4
