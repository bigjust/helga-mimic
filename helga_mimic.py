import markovify
import time

from helga import settings, log
from helga.db import db
from helga.plugins import command, match

from cobe.brain import Brain

DEBUG = getattr(settings, 'HELGA_DEBUG', False)
OPS = getattr(settings, 'OPERATORS', [])
STATE_SIZE = int(getattr(settings, 'MIMIC_STATE_SIZE', 2))
GENERATE_TRIES = int(getattr(settings, 'MIMIC_GENERATE_TRIES', 50))
NICK = getattr(settings, 'NICK')

logger = log.getLogger(__name__)

brain = Brain('aineko.ai')

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

def train_brain(channel, filename='helga.ai'):

    start = time.time()

    brain = Brain(filename)

    brain.start_batch_learning()

    for line in db.logger.find({
        'channel': channel,
    }):
        brain.learn(line['message'])

    brain.stop_batch_learning()


@match(r'aineko')
@command('mimic', help='mimics nick or channel specified')
def mimic(client, channel, nick, message, *args):

    # you talkin' to me?
    if len(args) == 1:
        #return 'matched! args={}'.format(args)
        # Match - args[0] is return value of check(), re.findall
        found_list = args[0]

        brain = Brain('helga.ai')
        reply = brain.reply(message)

        return reply

    # mimic command
    if len(args) > 1:
        channel_or_nicks = args[1]

        if not args[1]:
            channel_or_nicks = [channel]

    if 'build' in channel_or_nicks:
        # retrain brain

        train_brain(channel)
        return 'Done.'

    start = time.time()
    generated = generate_sentence(channel_or_nicks)
    duration = time.time() - start

    if not generated:
        return 'i got nothing :/'

    if DEBUG:
        generated = "{} [{:.2f}s]".format(generated, duration)

    return generated
