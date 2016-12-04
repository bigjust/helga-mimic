import markovify
import os
import time

from helga import settings, log
from helga.db import db
from helga.plugins import command, match, ResponseNotReady

from cobe.brain import Brain
from twisted.internet import reactor

DEBUG = getattr(settings, 'HELGA_DEBUG', False)
OPS = getattr(settings, 'OPERATORS', [])
STATE_SIZE = int(getattr(settings, 'MIMIC_STATE_SIZE', 2))
GENERATE_TRIES = int(getattr(settings, 'MIMIC_GENERATE_TRIES', 50))
NICK = getattr(settings, 'NICK')

logger = log.getLogger(__name__)


def is_channel_or_nick(channel_or_nick):
    """
    Returns `True` if channel, `False` if nick.
    """

    return channel_or_nick.startswith('#')

def generate_model(channel_or_nick):
    """
    Generates a markov chain for channel or nick
    """

    logger.debug('generating model for {}'.format(channel_or_nick))

    db_filter = {}

    if is_channel_or_nick(channel_or_nick):
        db_filter = {'channel': channel_or_nick}
    else:
        db_filter = {'nick': channel_or_nick}

    logger.debug('db_filter: {}'.format(db_filter))
    logger.debug('{} lines found'.format(db.logger.find(db_filter).count()))

    corpus = ''
    for doc in db.logger.find(db_filter):
        corpus += doc['message']
        corpus += '\n'

    return markovify.NewlineText(corpus, state_size=STATE_SIZE)


def generate_sentence(channel_or_nicks):
    """
    Generates a sentence from the corpus of `channel_or_nick`

    """

    logger.debug('generating sentence for {}'.format(channel_or_nicks))

    models = []

    for channel_or_nick in channel_or_nicks:
        models.append(generate_model(channel_or_nick))

    return markovify.combine(models).make_sentence(
        tries=GENERATE_TRIES
    )

def train_brain(client, channel):

    # replace the current brain
    os.remove('brain.ai')
    BRAIN = Brain('brain.ai')

    start = time.time()

    BRAIN.start_batch_learning()

    for line in db.logger.find({
        'channel': channel,
    }):
        BRAIN.learn(line['message'])

    BRAIN.stop_batch_learning()

    logger.debug('learned stuff. Took {:.2f}s'.format(
        time.time() - start
    ))

    client.msg(channel, "I learned some stuff!")

@match(r'{}'.format(NICK))
@command('mimic', help='mimics nick or channel specified')
def mimic(client, channel, nick, message, *args):

    BRAIN = Brain('brain.ai')

    # you talkin' to me?
    if len(args) == 1:
        # Match - args[0] is return value of check(), re.findall
        found_list = args[0]
        return BRAIN.reply(message.replace('aineko',''))

    # mimic command
    if len(args) > 1:
        channel_or_nicks = args[1]

        if not args[1]:
            channel_or_nicks = [channel]

    if 'build' in channel_or_nicks:
        # learn some shit
        reactor.callLater(0, train_brain, client, channel)
        raise ResponseNotReady

    start = time.time()
    generated = generate_sentence(channel_or_nicks)
    duration = time.time() - start

    if not generated:
        return 'i got nothing :/'

    if DEBUG:
        generated = "{} [{:.2f}s]".format(generated, duration)

    return generated
