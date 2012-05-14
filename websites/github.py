#
# tinybot plugin for github.com
#
# - Initial support added for commits messages
#

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
               "reponame [shortsha1hash] Short commit message."

        """
        parts = url.split("/")
        reponame = parts[4]
        sha1 = parts[-1][:5]
        msg = ""

        index = page.find('<div class="commit full-commit ">')
        if (index == -1):
                return None

        # Take the first sentence of the commit log between the <pre> tags 
        match = re.match(r'.*?<p class="commit-title">(.*?)</p>', page[index:], re.DOTALL)
        if match:
                msg = match.group(1).strip()

        return "%s [%s] %s." % (reponame, sha1, msg)

def get_tree_summary(url, page):
        """ Generate a summary of a tree.

            Returns a string of the form:
                "user's reponame: project summary"
        """
        parts = url.split("/")
        username = parts[3]
        reponame = parts[4]
        summary = "A git repository on github.com"

        match = re.match(r'.*?<meta name="description" content="(.*?)"', page, re.DOTALL)
        if match:
                summary = clean(match.group(1))

        return "%s's %s: %s" % (username, reponame, summary)

def get_summary(url, page):
        """ Figure out what kind of page this is and dispatch to the
            appropriate handler.
        """

        parts = url.split("/")
        if (len(parts) < 6):
                return None
        username = parts[3]
        reponame = parts[4]
        type = parts[5]

        if type == "commit":
                return get_commit_summary(url, page)
        elif type == "tree" or type == "commits":
                return get_tree_summary(url, page)

        # Unhandled page type, return default summary
        return None

if __name__ == "__main__":
        import sys
        f = open(sys.argv[1], "r")
        print get_summary("http://github.com/scottr/tinybot/tree/4171b7e9cf1edd782a8c5fb5af1a3a581b8f4610", f.read())
        f.close()


