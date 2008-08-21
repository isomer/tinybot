
mimetype="text/plain"

def get_summary(url, file):
	fp = open(file, "r")
	head=fp.read(100)
	head = head.replace("\n", " ").replace("\r", "")
	return head
