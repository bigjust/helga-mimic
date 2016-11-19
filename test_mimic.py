import unittest

from helga_mimic import is_channel_or_nick


class ChannelOrNickTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_channel(self):
        """
        is_channel_or_nick returns `True` for channels
        """

        self.assertTrue(is_channel_or_nick('#test'))
        self.assertTrue(is_channel_or_nick('##test-ot'))

    def test_nick(self):
        """
        is_channel_or_nick returns `False` for nicks
        """

        self.assertFalse(is_channel_or_nick('aineko'))
