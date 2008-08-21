import glob
import re
import mimetypes

summary_generators={}

for file in glob.glob("filetypes/*.py"):
	if not file.endswith("__init__.py"):
		x = __import__(file[:-2])
		if "get_summary" in dir(x) and "mimetype" in dir(x):
			summary_generators[x.mimetype]=x.get_summary

def get_summary(url, file):
	(type, encoding) = mimetypes.guess_type(url)
#	print "mimetype",type

	if type is None:
		return None
	if type in summary_generators:
		return summary_generators[type](url, file)
	widetype = type.split("/")[0]+"/*"
#	print "trying harder:",widetype
	if widetype in summary_generators:
		return summary_generators[widetype](url, file)

	return None
