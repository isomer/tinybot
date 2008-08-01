#!/usr/bin/python
# twisted imports
from twisted.protocols import irc
from twisted.internet import reactor, protocol

# system imports
import time, sys
import re
import random
import urllib

import tiny_settings
import tinyurl

class IsoBot(irc.IRCClient):
    
    def __init__(self):
        self.nickname = "tinybot"
        reactor.callLater(30,self.ping_pong)

    def ping_pong(self):
    	self.sendLine("PING :Ph33r!")
        reactor.callLater(30,self.ping_pong)

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)

    # callbacks for events

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        if tiny_settings.x_login:
            self.msg("x@channels.undernet.org", x_login)
        self.mode(self.nickname,'+','ix')
        for channel, key in tiny_settings.channels.items():
            self.join("#" + channel, key)

    def irc_unknown(self, prefix, command, params):
    	if command=="PONG":
            return
        if command=="396":
            pass
		# Commands to do on auth successful
 
    def notice(self, user, channel, msg):
    	print user,"NOTICE",channel,msg

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        print user,"PRIVMSG",channel,msg
        target=channel
        if target==self.nickname:
            target=user
        m=tinyurl.tiny(user,channel,msg)
        if m is not None: 
            while "\n" in m or "\r" in m:
                m=m.split("\r",1)[0]
                m=m.split("\n",1)[0]
            self.say(channel,m)
            print user,"PRIVMSG",channel,m
        if msg=="!tinybot":
            m=tinyurl.find_urls_by_channel(channel)
            for i in m:
                self.say(user,i)

class IsoBotFactory(protocol.ClientFactory):
    # the class of the protocol to build when new connection is made
    protocol = IsoBot

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        time.sleep(30)
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        time.sleep(30)
        connector.connect()


if __name__ == '__main__':
    # initialize logging
    
    # create factory protocol and application
    f = IsoBotFactory()

    # connect factory to this host and port
    reactor.connectTCP("eu.undernet.org", 6667, f)
    #reactor.connectTCP("amsterdam2.nl.eu.undernet.org", 6667, f)
    #reactor.connectTCP("stockholm.se.eu.undernet.org", 6667, f)
    #reactor.connectTCP(random.choice(
    #		["london2.uk.eu.undernet.org","london.uk.eu.undernet.org"]),
    #	 6667, f)

    # run bot
    reactor.run()

# vi:et:ts=4:sw=4
