#
# tinybot plugin for github.com
#
# - Initial support added for commits messages
#

import sys
import re

website = "github.com"

def clean(html):
        """strip html tags etc"""
        txt = re.sub('<[^>]+>', '', html)
        txt = txt.replace('&nbsp;', ' ').strip()
        return txt

def get_commit_summary(url, page):
        """ Generate a summary of a commit.

            Returns a string of the form:
               "reponame: [shortsha1hash] Short commit message"

        """
        sha1 = ""
        msg = ""
        parts = url.split("/")
        reponame = parts[4]
        sha1 = parts[-1][:5]

        index = page.find('<div class="message">')
        if (index == -1):
                print "message div not found"
                return None

        # Take the first sentence of the commit log between the <pre> tags 
        match = re.match(r".*?<pre>(.*?)</pre>", page[index:], re.DOTALL)
        if match:
                msg = clean(match.group(1))
                # git convention is to use the first sentence of the commit
                # message as a summary. Return everything up to the first
                # period.
                index = msg.find(".")
                if (index != -1):
                        msg = msg[:index]

        return "%s [%s] %s." % (reponame, sha1, msg)

def get_summary(url, page):
        """ Figure out what kind of page this is and dispatch to the
            appropriate handler.
        """

        if url.find("/commit/") != -1:
                return get_commit_summary(url, page);

        # Unhandled page type, return default summary
        return None

if __name__ == "__main__":
        f = open(sys.argv[1], "r")
        print get_summary("http://github.com/scottr/tinybot/commit/4171b7e9cf1edd782a8c5fb5af1a3a581b8f4610", f.read())
        f.close()


