import markovify

from helga import settings, log
from helga.db import db
from helga.plugins import command

OPS = getattr(settings, 'OPERATORS', [])

logger = log.getLogger(__name__)

def is_channel_or_user(channel_or_user):
    """
    Returns `True` if channel, `False` if user.
    """

    return channel_or_user.startswith('#')

def generate_sentence(channel_or_user):
    """
    Generates a sentence from the corpus of `channel_or_user`

    """

    db_filter = {}

    if is_channel_or_user(channel_or_user):
        db_filter = {'channel': channel_or_user}
    else:
        db_filter = {'nick': channel_or_user}

    logger.debug('{} lines found'.format(db.logger.find(db_filter).count()))

    corpus = ''
    for doc in db.logger.find(db_filter):
        corpus += doc['message']
        corpus += '\n'

    text_model = markovify.NewlineText(corpus, state_size=4)
    return text_model.make_sentence(tries=int(getattr(settings, 'MIMIC_TRIES', 50)))

@command('mimic', help='mimics user or channel specified')
def mimic(client, channel, nick, message, cmd, args):

    logger.debug('mimic initiated')

    if not args[0]:
        return 'must specify a thing'

    generated = generate_sentence(args[0])

    if not generated:
        return 'i got nothing :/'

    return generated
