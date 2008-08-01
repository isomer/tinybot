import time
import cgi
import urllib

import tiny_settings

def generate_atom(fname,entries):
	output=open(tiny_settings.atomdir + "%s.atom" % fname, "w")
	print >>output,"""<?xml version="1.0" encoding="utf-8"?>

	<feed xmlns="http://www.w3.org/2005/Atom">
	   <title>Tinybot URL harvester</title>
	   <link href="%(dir)s%(fname)s.atom" rel="self"/>
	   <updated>%(now)s</updated>
	   <id>http://coders.meta.net.nz/~perry/tinybot/</id>""" % {
        "dir" : tiny_settings.atomdir_url,
		"now" : time.strftime("%Y-%m-%dT%H:%M:%SZ"),
		"fname" : urllib.quote(fname)
	}

	for (updatedts,title,author,url,id,summary) in entries:
		print >>output,"""
		  <entry>
		     <title>%(title)s</title>
		     <author>
			<name>%(author)s</name>
		     </author>
		     <link href="%(url)s"/>
		     <id>%(id)s</id>
		     <updated>%(updatedts)s</updated>
		     <summary type="html">%(summary)s</summary>
		   </entry>
		""" % {
			"title" : cgi.escape(title),
			"author" : cgi.escape(author),
			"url" : cgi.escape(url),
			"id" : cgi.escape(id),
			"updatedts" : time.strftime("%Y-%m-%dT%H:%M:%SZ",
					time.gmtime(updatedts)),
			"summary" : cgi.escape(summary),
		}

	print >>output,"""
	</feed>
	"""
