import markovify

from helga import settings, log
from helga.db import db
from helga.plugins import command

OPS = getattr(settings, 'OPERATORS', [])
STATE_SIZE = int(getattr(settings, 'MIMIC_STATE_SIZE', 2))
GENERATE_TRIES = int(getattr(settings, 'MIMIC_GENERATE_TRIES', 50))

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

@command('mimic', help='mimics nick or channel specified')
def mimic(client, channel, nick, message, cmd, args):

    if not args:
        channel_or_nicks = [channel]
    else:
        channel_or_nicks = args

    generated = generate_sentence(channel_or_nicks)

    if not generated:
        return 'i got nothing :/'

    return generated
