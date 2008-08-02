#!/usr/bin/python
# twisted imports
from twisted.protocols import irc
from twisted.internet import reactor, protocol

# system imports
import time, sys
import re
import urllib

import tiny_settings
import tinyurl

class IsoBot(irc.IRCClient):
    
    def __init__(self):
        self.nickname = tiny_settings.nickname
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
        self.mode(self.nickname, '+', 'ix')
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
        print user, "PRIVMSG", channel, msg
        if channel == 'AUTH' or user.lower().endswith("undernet.org"):
            # server message during connect
            return
        target = channel # where to send reply
        reply = None
        if target == self.nickname:
            # this message was sent to us rather than a channel
            target = user
            if msg == 'help':
                reply = 'type "!tinybot" in a channel to see recently pasted links\n'
                url = tiny_settings.atomdir_url
                reply += 'see %s%%23$channel.atom for a full list' % url
                reply += ' (obviously replacing "$channel" with the appropriate name)'
            else:
                reply = 'huh? try "help"'
        else:
            # see if this message should get a response
            reply = tinyurl.tiny(user, channel, msg)
            if reply is not None: 
                # get 1st line only, if we have multi-line response
                while "\n" in reply or "\r" in reply:
                    reply=reply.split("\r",1)[0]
                    reply=reply.split("\n",1)[0]
        if reply is not None: 
            print "PRIVMSG reply", target, reply
            for line in reply.split("\n"):
                # channel messages will already be set to single line (above),
                # so we'll only send multiline responses to a user
                self.msg(target, line)
        if msg == "!tinybot" and target != user:
            # posted to a channel, reply to user
            m = tinyurl.find_urls_by_channel(channel) or ("no recent links",)
            for i in m:
                self.msg(user, i)

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
    name, ip = tiny_settings.ircserver
    print "connecting to %s:%d" % (name, ip)
    reactor.connectTCP(name, ip, f)

    # run bot
    reactor.run()

# vi:et:ts=4:sw=4
