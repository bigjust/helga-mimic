import markovify
import os
import requests
import time

from helga import settings, log
from helga.db import db
from helga.plugins import Command, ResponseNotReady

from helga_alias import find_aliases
from helga_twitter import tweet

from cobe.brain import Brain
from twisted.internet import reactor

DEBUG = getattr(settings, 'HELGA_DEBUG', False)
GENERATE_TRIES = int(getattr(settings, 'MIMIC_GENERATE_TRIES', 50))
IGNORED = getattr(settings, 'IGNORED', [])
NICK = getattr(settings, 'NICK')
OPS = getattr(settings, 'OPERATORS', [])
STATE_SIZE = int(getattr(settings, 'MIMIC_STATE_SIZE', 2))
THINK_TIME = int(getattr(settings, 'MIMIC_THINK_TIME', 2000))

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

        logger.debug('reconstituting model for {}'.format(model['key']))

        models.append(
            markovify.NewlineText.from_json(model['model'])
        )

        channel_or_nicks.pop(channel_or_nicks.index(model['key']))

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


class MimicPlugin(Command):

    command = 'mimic'

    last_response = ''

    def preprocess(self, client, channel, nick, message):
        if NICK in message:
            response = bot_say(seed=message)
            client.msg(channel, response)

            self.last_response = response

        return channel, nick, message

    def run(self, client, channel, nick, message, cmd, args):

        logger.debug('args: {}'.format(args))
        logger.debug('cmd: {}'.format(cmd))

        if not args:
            args = [channel]

        channel_or_nicks = args

        if 'tweet' in channel_or_nicks:
            logger.debug(u'sending tweet: {}'.format(self.last_response))
            reactor.callLater(0, tweet, client, channel, self.last_response)
            raise ResponseNotReady

        if 'build' in channel_or_nicks:
            reactor.callLater(0, train_brain, client, channel)
            raise ResponseNotReady

        if 'load' in channel_or_nicks:

            if len(args) < 3:
                return 'usage: !mimic load <key> <url>'

            key = str(args[1])
            resp = requests.get(args[2])

            for line in resp.content.splitlines():

                markov_model = markovify.NewlineText(
                    resp.content,
                    state_size=STATE_SIZE
                )

                db.mimic.replace_one({
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

        self.last_response = generated

        if DEBUG:
            generated = u"{} [{:.2f}s]".format(generated, duration)

        return generated
