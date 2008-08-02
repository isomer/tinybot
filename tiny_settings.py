import random

# irc server (servername, ip) to try connecting to
# TODO - can't figure out how to get twisted connectTCP to fall back to
# another if the first fails...
ircserver = ("eu.undernet.org", 6667)
# ircserver = ("amsterdam2.nl.eu.undernet.org", 6667)
# ircserver = ("stockholm.se.eu.undernet.org", 6667)
# ircserver = (random.choice(["london2","london"]) + ".uk.eu.undernet.org", 6667)

# what name to try to use when connected
nickname = 'tinybot-test'

# "channelname": "key" (or None)
channels = {
    'tinybottest': None,
}

# a string used for logging in after connecting... eg "login username password"
x_login = None

# where to write the files, one per channel (with a trailing slash)
atomdir = "/home/perry/public_html/tinybot/"
#atomdir = "/tmp/"

# url to this directory (with a trailing slash)
atomdir_url = "http://coders.meta.net.nz/~perry/tinybot/"
