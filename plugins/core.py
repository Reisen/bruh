"""
    This plugin is one of the earliest plugins to be loaded. It takes a server
    object and patches it at runtime to include some extra useful methods that
    will allow other plugins to more easily use the IRC protocol.
"""
from plugins import event
from plugins.commands import command
from plugins.authentication import authenticated


def reply(self, message):
    """Replies to the channel a message was sent from."""
    prefix, command, args = self.parsed_message

    # Determine whether the message was from a query, or a channel.
    target = args[0] if args[0].startswith('#') else prefix.split('!')[0]
    self.raw('PRIVMSG {} :{}\r\n'.format(target, message))


def say(self, channel, message):
    """Sends a message to the channel the event was received from."""
    self.raw('PRIVMSG {} :{}\r\n'.format(channel, message))


def notice(self, user, message):
    """Sends a notice to the channel an event was received from"""
    self.raw('NOTICE {} :{}\r\n'.format(user, message))


def action(self, channel, message):
    """Sends an action message to a target channel."""
    self.raw('PRIVMSG {} :\01ACTION {}\01\r\n'.format(channel, message))


def join(self, channel):
    """Join a target channel."""
    self.raw('JOIN {}\r\n'.format(channel))


def part(self, channel):
    """Leaves a channel."""
    self.raw('PART {}\r\n'.format(channel))


@event('BRUH')
def addCoreFunctionality(irc):
    """
    Called when a server is first created, and adds our new userful methods to
    the object for use in other plugins.
    """
    container = type(irc)

    # Bind the new methods to the IRC class
    container.reply  = reply
    container.say    = say
    container.notice = notice
    container.action = action
    container.join   = join
    container.part   = part


# Implement commands wrapping core functionality of the bot. Allows controlling
# the bot more easily for regular IRC like behaviour.
@command(['say'])
@authenticated(['Admin', 'Moderator'])
def _say(irc, nick, chan, msg, args, user):
    target, msg = msg.split(' ', 1)
    irc.say(target, msg)


@command(['notice'])
@authenticated(['Admin', 'Moderator'])
def _notice(irc, nick, chan, msg, args, user):
    target, msg = msg.split(' ', 1)
    irc.notice(target, msg)


@command(['action'])
@authenticated(['Admin', 'Moderator'])
def _action(irc, nick, chan, msg, args, user):
    target, msg = msg.split(' ', 1)
    print(repr(msg))
    irc.action(target, msg)


@command(['join'])
@authenticated(['Admin', 'Moderator'])
def _join(irc, nick, chan, msg, args, user):
    irc.join(msg)


@command(['part'])
@authenticated(['Admin', 'Moderator'])
def _part(irc, nick, chan, msg, args, user):
    irc.part(msg)


@command(['kick'])
@authenticated(['Admin', 'Moderator'])
def _kick(irc, nick, chan, msg, args, user):
    target, *msg = msg.split(' ', 1)
    msg = 'Requested' if not msg else msg[0]
    irc.send('KICK {} {} :{}'.format(chan, target, msg))


@command(['op'])
@authenticated(['Admin', 'Moderator'])
def _admin(irc, nick, chan, msg, args, user):
    irc.send('MODE {} +o {}'.format(chan, msg))


@command(['voice'])
@authenticated(['Admin', 'Moderator'])
def _voice(irc, nick, chan, msg, args, user):
    irc.send('MODE {} +v {}'.format(chan, msg))


# Preferably, don't use this. Adding it to test things on my own personal IRC
# instance. The bot being in oper mode is just bad news.
@command(['oper'])
@authenticated(['Admin', 'Moderator'])
def _operator(irc, nick, chan, msg, args, user):
    irc.send('OPER {}'.format(msg))
