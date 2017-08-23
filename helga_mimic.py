import markovify
import os
import requests
import time

from helga import settings, log
from helga.db import db
from helga.plugins import command, match, ResponseNotReady

from helga_alias import find_aliases

from cobe.brain import Brain
from twisted.internet import reactor

DEBUG = getattr(settings, 'HELGA_DEBUG', False)
OPS = getattr(settings, 'OPERATORS', [])
STATE_SIZE = int(getattr(settings, 'MIMIC_STATE_SIZE', 2))
GENERATE_TRIES = int(getattr(settings, 'MIMIC_GENERATE_TRIES', 50))
THINK_TIME = int(getattr(settings, 'MIMIC_THINK_TIME', 2000))
NICK = getattr(settings, 'NICK')
MODELS = {}

IGNORED = getattr(settings, 'IGNORED', [])

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

    db_filter = {
        'nick': {'$nin': IGNORED},
        'message': {'$regex': '^(?!\.|\,|\!)'},
    }

    if is_channel_or_nick(channel_or_nick):
        db_filter = {'channel': channel_or_nick}
    else:
        db_filter = {'nick': channel_or_nick}

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
    nicks = [str(nick) for nick in channel_or_nicks]

    db_filter = {
        'key': {
            '$in': nicks,
        }}

    logger.debug('db filter: {}'.format(db_filter))

    for model in db.mimic.find(db_filter):

        models.append(
            markovify.NewlineText.from_json(model['model'])
        )

    for channel_or_nick in channel_or_nicks:
        if is_channel_or_nick(channel_or_nick):
            models.append(generate_model(channel_or_nick))
        else:
            for alias in find_aliases(channel_or_nick):
                models.append(generate_model(alias))

    return markovify.combine(models).make_sentence(
        tries=GENERATE_TRIES
    )

def train_brain(client, channel):

    logger.debug('starting training')
    logger.debug('ignored: {}'.format(IGNORED))

    # replace the current brain
    try:
        os.remove('brain.ai')
    except:
        pass

    BRAIN = Brain('brain.ai')

    logger.debug('created brain.ai')

    start = time.time()

    BRAIN.start_batch_learning()

    logger_lines = db.logger.find({
        'channel': channel,
        'nick': {'$nin': IGNORED},
        'message': {'$regex': '^(?!\.|\,|\!)'},
    })

    logger.debug('log total: {}'.format(logger_lines.count()))

    for line in logger_lines:
        BRAIN.learn(line['message'])

    BRAIN.stop_batch_learning()

    logger.debug('learned stuff. Took {:.2f}s'.format(
        time.time() - start
    ))

    client.msg(channel, "I learned some stuff!")

# API
def bot_say(seed='', think_time=THINK_TIME):
    """

    Generate response from cobe, seeding with the message.

    The we do some processing on the out, like removing nicks (both
    active and known), or replacing nick mentions with OP or preset
    list.

    1. remove nicks (both active and known), replace with either OP or
    something from a preset list TODO

    2. remove odd number quotes (the first)

    3. TODO
    """

    response = Brain('brain.ai').reply(
        seed.replace(NICK,''),
        loop_ms=think_time,
    )

    balance_chars = ['"', '\'']
    remove_chars = ['[', ']', '{', '}', '(', ')']

    for char in remove_chars:
        response = response.replace(char, '')

    for char in balance_chars:
        if response.count(char) % 2:
            response = response.replace(char, '', 1)

    return response

@match(r'{}'.format(NICK))
@command('mimic', help='mimics nick or channel specified')
def mimic(client, channel, nick, message, *args):

    logger.debug('args: {}'.format(args))

    # you talkin' to me?
    if len(args) == 1:
        # Match - args[0] is return value of check(), re.findall
        return bot_say(seed=message)

    # mimic command
    if len(args) > 1:
        channel_or_nicks = args[1]

        if 'build' in channel_or_nicks:
            reactor.callLater(0, train_brain, client, channel)
            raise ResponseNotReady

        if 'load' in channel_or_nicks:

            cmd_args = channel_or_nicks
            if len(cmd_args) < 3:
                return 'usage: !mimic load <key> <url>'

            key = str(cmd_args[1])
            resp = requests.get(cmd_args[2])

            for line in resp.content.splitlines():

                markov_model = markovify.NewlineText(
                    resp.content,
                    state_size=STATE_SIZE
                )

                result = db.mimic.replace_one(
                    {
                        'key': key,
                    },{
                        'key': key,
                        'model': markov_model.to_json(),
                    },
                    True
                )

                return '{} loaded.'.format(key)

        start = time.time()
        generated = generate_sentence(channel_or_nicks)
        duration = time.time() - start

        if not generated:
            return 'i got nothing :/'

        if DEBUG:
            generated = u"{} [{:.2f}s]".format(generated, duration)

        return generated
